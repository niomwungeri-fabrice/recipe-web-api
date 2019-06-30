from django.test import TestCase
from django.contrib.auth import get_user_model


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
