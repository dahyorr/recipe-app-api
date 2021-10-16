from django.contrib.auth import get_user_model
from django.test import TestCase
from core import models


def sample_user(email='test@test.com', password='testtest'):
    """create a sample user"""
    return get_user_model().objects.create_user(email, password)


class ModelTests(TestCase):

    def test_create_user_with_email_successful(self):
        """Test user creation"""
        email = 'test@test.com'
        password = 'testtest'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
            )
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test new user email is normalized"""
        email = 'test@TEST.com'
        user = get_user_model().objects.create_user(email, 'idnfsnj')
        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """Test Creating user with no email raises error"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'idnfsnj')

    def test_tag_str(self):
        """Test the tag string representation"""
        tag = models.Tag.objects.create(
            user=sample_user(),
            name='Vegan'
        )
        self.assertEqual(str(tag), tag.name)
