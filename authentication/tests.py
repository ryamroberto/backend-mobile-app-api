from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class AuthTests(APITestCase):
    def setUp(self):
        cache.clear()
        self.user_data = {
            "email": "testuser@example.com",
            "password": "testpassword123",
        }
        self.user = User.objects.create_user(**self.user_data)

    def test_register_user(self):
        url = reverse("register")
        data = {
            "email": "newuser@example.com",
            "password": "newpassword123",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 2)

    def test_login_user(self):
        url = reverse("token_obtain_pair")
        response = self.client.post(url, self.user_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_refresh_token(self):
        url_login = reverse("token_obtain_pair")
        response_login = self.client.post(url_login, self.user_data, format="json")
        refresh_token = response_login.data["refresh"]

        url_refresh = reverse("token_refresh")
        response_refresh = self.client.post(url_refresh, {"refresh": refresh_token}, format="json")
        self.assertEqual(response_refresh.status_code, status.HTTP_200_OK)
        self.assertIn("access", response_refresh.data)

    def test_logout_user(self):
        url_login = reverse("token_obtain_pair")
        response_login = self.client.post(url_login, self.user_data, format="json")
        refresh_token = response_login.data["refresh"]
        access_token = response_login.data["access"]

        url_logout = reverse("logout")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        response_logout = self.client.post(url_logout, {"refresh": refresh_token}, format="json")
        self.assertEqual(response_logout.status_code, status.HTTP_205_RESET_CONTENT)

        url_refresh = reverse("token_refresh")
        self.client.credentials()
        response_refresh = self.client.post(url_refresh, {"refresh": refresh_token}, format="json")
        self.assertEqual(response_refresh.status_code, status.HTTP_401_UNAUTHORIZED)

    @override_settings(DISABLE_THROTTLING=False)
    def test_auth_throttling(self):
        url = reverse("token_obtain_pair")
        data = {
            "email": "throttle@example.com",
            "password": "any",
        }

        for _ in range(5):
            self.client.post(url, data, format="json")

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
