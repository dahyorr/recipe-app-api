from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from core.models import Ingredient
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

    # def test_create_ingredient_successful(self):
    #     """test creating a new ingredient"""
    #     payload = {'name': 'Test ingredient'}
    #     res = self.client.post(INGREDIENTS_URL, payload)
    #     self.assertEqual(res.status_code, status.HTTP_201_CREATED)
    #     exists = Ingredient.objects.filter(
    #         user=self.user,
    #         name=payload['name']
    #         ).exists
    #     self.assertTrue(exists)

    # def test_create_invalid_ingredient(self):
    #     """test creating a new ingredient with invalid payload"""
    #     payload = {'name': ''}
    #     res = self.client.post(INGREDIENTS_URL, payload)
    #     self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
