from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from django.core.cache import cache

User = get_user_model()

class AuthTests(APITestCase):
    def setUp(self):
        cache.clear()

    def test_register_user(self):
        """
        Garante que podemos criar um novo usuário.
        """
        url = reverse('register')
        data = {
            'email': 'test@example.com',
            'password': 'testpassword123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_login_user(self):
        """
        Garante que podemos fazer login e obter tokens JWT.
        """
        User.objects.create_user(email='login@example.com', password='loginpassword123')
        
        url = reverse('token_obtain_pair')
        data = {
            'email': 'login@example.com',
            'password': 'loginpassword123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_logout_user(self):
        """
        Garante que podemos fazer logout e o refresh token é invalidado.
        """
        User.objects.create_user(email='logout@example.com', password='logoutpassword123')
        
        # Login
        login_url = reverse('token_obtain_pair')
        login_data = {'email': 'logout@example.com', 'password': 'logoutpassword123'}
        login_response = self.client.post(login_url, login_data, format='json')
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)

        refresh_token = login_response.data['refresh']
        access_token = login_response.data['access']
        
        # Logout
        logout_url = reverse('logout')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        logout_response = self.client.post(logout_url, {'refresh': refresh_token}, format='json')
        self.assertEqual(logout_response.status_code, status.HTTP_205_RESET_CONTENT)

        # Tentar usar o refresh token após logout deve falhar
        refresh_url = reverse('token_refresh')
        self.client.credentials() 
        refresh_response = self.client.post(refresh_url, {'refresh': refresh_token}, format='json')
        self.assertEqual(refresh_response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_auth_throttling(self):
        """
        Garante que o limite de requisições para autenticação funciona.
        O limite default em settings é 5/minute.
        """
        url = reverse('token_obtain_pair')
        data = {
            'email': 'throttle@example.com',
            'password': 'any'
        }
        
        for _ in range(5):
            self.client.post(url, data, format='json')
            
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)