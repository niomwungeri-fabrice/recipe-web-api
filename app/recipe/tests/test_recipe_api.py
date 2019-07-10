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

    def test_create_basic_recipe(self):
        payload = {
            'title': 'Sample recipe title',
            'time_minutes': 7,
            'price': 400
        }

        res = self.client.post(RECIPE_ROUTE, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_create_recipe_with_tags(self):
        tag1 = sample_tag(user=self.user, name='tag1')
        tag2 = sample_tag(user=self.user, name='tag2')

        payload = {
            'title': 'Sample recipe title',
            'time_minutes': 7,
            'price': 400,
            'tags': [tag1.id, tag2.id]
        }
        res = self.client.post(RECIPE_ROUTE, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        tags = recipe.tags.all()
        self.assertEqual(tags.count(), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_create_recipe_with_ingredients(self):
        ingredient1 = sample_ingredient(user=self.user, name='ingredient1')
        ingredient2 = sample_ingredient(user=self.user, name='ingredient2')

        payload = {
            'title': 'Sample recipe title',
            'time_minutes': 7,
            'price': 400,
            'ingredients': [ingredient1.id, ingredient2.id]
        }
        res = self.client.post(RECIPE_ROUTE, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        ingredients = recipe.ingredients.all()
        self.assertEqual(ingredients.count(), 2)
        self.assertIn(ingredient1, ingredients)
        self.assertIn(ingredient2, ingredients)

    # def test_partial_update_recipe(self):
    #     recipe = sample_recipe(user=self.user)
    #     recipe.tags.add(sample_tag(user=self.user))
    #     new_tag = sample_tag(user=self.user, name='test sample tag')

    #     payload = {
    #         'title': 'updated recipe title',
    #         'tags': [new_tag.id]
    #     }
    #     url = generate_detail_route(recipe.id)
    #     self.client.patch(url, payload)

    #     recipe.refresh_from_db()
    #     print(recipe.title, "====")
    #     self.assertEqual(recipe.title, payload['title'])
    #     tags = recipe.tags.all()
    #     self.assertEqual(len(tags), 1)
    #     self.assertIn(new_tag, tags)

    # # def test_full_update_recipe(self):
    # #     recipe = sample_recipe(user=self.user)
    # #     recipe.tags.add(sample_tag(user=self.user))

    # #     payload = {
    # #         'title': 'update recipe title',
    # #         'time_minutes': 89,
    # #         'price': 900

    # #     }
    # #     url = generate_detail_route(recipe.id)
    # #     self.client.put(url, payload)

    # #     recipe.refresh_from_db()
    # #     self.assertEqual(recipe.title, payload['title'])
    # #     tags = recipe.tags.all()
    # #     self.assertEqual(len(tags), 0)
