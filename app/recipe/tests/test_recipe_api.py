from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe, Tag, Ingredient
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

RECIPE_ROUTE = reverse('recipe:recipe-list')


def generate_detail_route(recipe_id):
    return reverse('recipe:recipe-detail', args=[recipe_id])


def sample_ingredient(user, name='ingredient test 1'):
    return Ingredient.objects.create(user=user, name=name)


def sample_tag(user, name='tag test 1'):
    return Tag.objects.create(user=user, name=name)


def sample_recipe(user, **kwargs):
    defaults = {
        'title': 'Sample recipe title',
        'time_minutes': 5,
        'price': 120.00
    }
    defaults.update(kwargs)
    return Recipe.objects.create(user=user, **defaults)


class RecipeApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        res = self.client.get(RECIPE_ROUTE)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create(
            email='admin@email.com',
            password='password123'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_fetch_recipes(self):
        sample_recipe(user=self.user)
        sample_recipe(user=self.user)

        res = self.client.get(RECIPE_ROUTE)

        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_fetch_your_recipes_only(self):
        user2 = get_user_model().objects.create(
            email='admin2@email.com',
            password='password123'
        )
        sample_recipe(user=user2)
        sample_recipe(user=self.user, link='https://recipes.com')

        res = self.client.get(RECIPE_ROUTE)

        recipes = Recipe.objects.filter(user=self.user).order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data[0]['link'], 'https://recipes.com')
        self.assertEqual(res.data, serializer.data)

    def test_view_recipe_detail(self):
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        recipe.ingredients.add(sample_ingredient(user=self.user))

        url = generate_detail_route(recipe.id)
        res = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)
