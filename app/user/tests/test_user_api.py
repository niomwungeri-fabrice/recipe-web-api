from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_ROUTE = reverse('user:create')
TOKEN_ROUTE = reverse('user:token')
TOKEN_URL = reverse('user:token')


def create_user(**kwargs):
    return get_user_model().objects.create(**kwargs)


class UserAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.payload = {
            'email': 'user@email.com',
            'password': 'password123',
            'name': 'test user'
        }

    def test_create_user_successfully(self):
        res = self.client.post(CREATE_USER_ROUTE, self.payload)
        user = get_user_model().objects.get(**res.data)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(user.check_password(self.payload['password']))

    def test_user_already_exists(self):
        create_user(**self.payload)
        res = self.client.post(CREATE_USER_ROUTE, self.payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        self.payload['password'] = 'et'
        res = self.client.post(CREATE_USER_ROUTE, self.payload)
        user_exists = get_user_model().objects.filter(
            email=self.payload['email']
        ).exists()

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(user_exists)

    # def test_create_token_successfully(self):
    #     payload = {'email': 'user@email.com', 'password': 'password123'}
    #     create_user(**payload)
    #     res = self.client.post(TOKEN_ROUTE, payload)
    #     self.assertIn('token', res.data)
    #     self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_user_invalid_credentials(self):
        create_user(**self.payload)
        self.payload['password'] = 'wrong password!'
        res = self.client.post(TOKEN_ROUTE, self.payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        res = self.client.post(TOKEN_ROUTE, self.payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_password(self):
        self.payload['password'] = ''
        res = self.client.post(TOKEN_ROUTE, self.payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
