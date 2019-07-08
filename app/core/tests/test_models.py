from django.test import TestCase
from django.contrib.auth import get_user_model
from core import models


def sample_user(email="admin@email.com", password='password123'):
    """Helper functions to create a new user in db"""
    return get_user_model().objects.create_user(email, password)


class ModelTests(TestCase):
    def test_user_creation_successfully(self):
        email = "admin@email.com"
        password = "Password123"
        user = get_user_model().objects.create_user(
            email=email, password=password
        )

        self.assertTrue(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_email_normalized(self):
        email = "admin@EMAIL.COM"
        user = get_user_model().objects.create_user(
            email, 'password123')
        self.assertEqual(user.email, email.lower())

    def test_user_with_invalid_email(self):
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(
                None, '2489284kdjf')

    def test_user_is_super_user(self):
        user = get_user_model().objects.create_superuser(
            'admin@email.com', 'pass1234')

        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_create_str_tag(self):
        tag = models.Tag.objects.create(
            user=sample_user(),
            name='test_tag'
        )
        self.assertEqual(str(tag), tag.name)

    def test_create_str_ingredient(self):
        ingredient = models.Ingredient.objects.create(
            user=sample_user(),
            name='test_ingredient'
        )
        self.assertEqual(str(ingredient), ingredient.name)

    def test_create_recipe_str(self):
        recipe = models.Recipe.objects.create(
            user=sample_user(),
            title='Recipe title',
            time_minutes=7,
            price=30.00
        )
        self.assertEqual(str(recipe), recipe.title)
