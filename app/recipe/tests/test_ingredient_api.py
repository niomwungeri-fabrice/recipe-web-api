from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient
from recipe.serializers import IngredientSerializer

INGREDIENT_ROUTE = reverse('recipe:ingredient-list')


class IngredientApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        res = self.client.get(INGREDIENT_ROUTE)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientApiTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create(
            email='admin@email.com',
            password='password123'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_fetch_ingredient_list(self):
        Ingredient.objects.create(user=self.user, name='ingredient 1')
        Ingredient.objects.create(user=self.user, name='ingredient 2')

        res = self.client.get(INGREDIENT_ROUTE)
        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(res.data, serializer.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_your_ingredient_only(self):
        user2 = get_user_model().objects.create_user(
            email='admin2@email.com',
            password='password123'
        )
        Ingredient.objects.create(user=user2, name='ingredient 1')
        ingredient = Ingredient.objects.create(
            user=self.user, name='ingredient 2')

        res = self.client.get(INGREDIENT_ROUTE)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)

    # def test_create_tag_successfully(self):
    #     payload = {"name": "test ingredient"}
    #     self.client.post(INGREDIENT_ROUTE, payload)

    #     exists = Tag.objects.filter(
    #         user=self.user,
    #         name=payload['name']
    #     ).exists()
    #     self.assertTrue(exists)

    # def test_create_tag_invalid(self):
    #     payload = {"name": " "}
    #     res = self.client.post(INGREDIENT_ROUTE, payload)
    #     self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
