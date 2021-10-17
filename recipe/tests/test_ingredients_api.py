from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from core.models import Ingredient, Recipe
from recipe.serializers import IngredientSerializer

INGREDIENTS_URL = reverse('recipe:ingredient-list')


class PublicIngredientApiTests(TestCase):
    """test the publicly available tags api"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """test that login is requiered for retriving tags"""
        res = self.client.get(INGREDIENTS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsApiTests(TestCase):
    """test the private ingredients api"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='test@test.com',
            password='testtest'
            )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrive_ingredients(self):
        """test retrieving ingredients"""
        Ingredient.objects.create(user=self.user, name="Kale")
        Ingredient.objects.create(user=self.user, name="Salt")
        res = self.client.get(INGREDIENTS_URL)
        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        """test that ingredients returend are for the authenticated user"""
        user2 = get_user_model().objects.create_user(
            'test2@test.com',
            'testtest'
        )
        Ingredient.objects.create(user=user2, name="Fruity")
        ingredient = Ingredient.objects.create(
            user=self.user,
            name="Comfort Food")
        res = self.client.get(INGREDIENTS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)

    def test_create_ingredient_successful(self):
        """test creating a new ingredient"""
        payload = {'name': 'Test ingredient'}
        res = self.client.post(INGREDIENTS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        exists = Ingredient.objects.filter(
            user=self.user,
            name=payload['name']
            ).exists()
        self.assertTrue(exists)

    def test_create_invalid_ingredient(self):
        """test creating a new ingredient with invalid payload"""
        payload = {'name': ''}
        res = self.client.post(INGREDIENTS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_ingredients_assigned_to_recipe(self):
        """test filtering ingredients by those assigned to recipe"""
        ingredient1 = Ingredient.objects.create(
            user=self.user, name='Apples'
            )
        ingredient2 = Ingredient.objects.create(
            user=self.user, name='Turkey'
            )
        recipe = Recipe.objects.create(
            title='Apple Crumble',
            time_minutes=5,
            price=10.00,
            user=self.user
        )
        recipe.ingredients.add(ingredient1)
        res = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})
        serializer1 = IngredientSerializer(ingredient1)
        serializer2 = IngredientSerializer(ingredient2)
        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_retrieve_ingredients_assigned_unique(self):
        """Test filtering ingredients by assigned returns unique items"""
        ingredient = Ingredient.objects.create(user=self.user, name='Eggs')
        Ingredient.objects.create(user=self.user, name='Cheese')
        recipe1 = Recipe.objects.create(
            title='Eggs Benedict',
            time_minutes=30,
            price=12.00,
            user=self.user
        )
        recipe1.ingredients.add(ingredient)
        recipe2 = Recipe.objects.create(
            title='COriander eggs on Toast',
            time_minutes=20,
            price=5.00,
            user=self.user
        )
        recipe2.ingredients.add(ingredient)
        res = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})
        self.assertEqual(len(res.data), 1)
