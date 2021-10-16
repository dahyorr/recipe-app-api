from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from core.models import Tag
from recipe.serializers import TagSerializer

TAGS_URL = reverse('recipe:tag-list')


class PublicTagsApiTests(TestCase):
    """test the publicly available tags api"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """test that login is requiered for retriving tags"""
        res = self.client.get(TAGS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTests(TestCase):
    """test the authorized user tags api"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='test@test.com',
            password='testtest'
            )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrive_tags(self):
        """test retrieving tags"""
        Tag.objects.create(user=self.user, name="Vegan")
        Tag.objects.create(user=self.user, name="Desert")
        res = self.client.get(TAGS_URL)
        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """test that tags returend are for the authenticated user"""
        user2 = get_user_model().objects.create_user(
            'test2@test.com',
            'testtest'
        )
        Tag.objects.create(user=user2, name="Fruity")
        tag = Tag.objects.create(user=self.user, name="Comfort Food")
        res = self.client.get(TAGS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)

    def test_create_tag_successful(self):
        """test creating a new Tag"""
        payload = {'name': 'Test Tag'}
        res = self.client.post(TAGS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        exists = Tag.objects.filter(
            user=self.user,
            name=payload['name']
            ).exists()
        self.assertTrue(exists)

    def test_create_invalid_tag(self):
        """test creating a new Tag with invalid payload"""
        payload = {'name': ''}
        res = self.client.post(TAGS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
