from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag
from recipe.serializers import TagSerializer

TAGS_ROUTE = reverse('recipe:tag-list')


class TagsApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        res = self.client.get(TAGS_ROUTE)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create(
            email='admin@email.com',
            password='password123'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_fetch_tag_list(self):
        Tag.objects.create(user=self.user, name='tag 1')
        Tag.objects.create(user=self.user, name='tag 2')

        res = self.client.get(TAGS_ROUTE)
        # -name means return in reverse order
        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(res.data, serializer.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_your_tags_only(self):
        user2 = get_user_model().objects.create_user(
            email='admin2@email.com',
            password='password123'
        )
        Tag.objects.create(user=user2, name='tag 1')
        tag = Tag.objects.create(user=self.user, name='tag 2')

        res = self.client.get(TAGS_ROUTE)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)

    def test_create_tag_successfully(self):
        payload = {"name": "test tag"}
        self.client.post(TAGS_ROUTE, payload)

        exists = Tag.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()
        self.assertTrue(exists)

    def test_create_tag_invalid(self):
        payload = {"name": " "}
        res = self.client.post(TAGS_ROUTE, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
