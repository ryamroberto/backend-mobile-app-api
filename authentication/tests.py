from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

User = get_user_model()

class AuthTests(APITestCase):
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
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get(email='test@example.com').email, 'test@example.com')

    def test_login_user(self):
        """
        Garante que podemos fazer login e obter tokens JWT.
        """
        # Primeiro, registrar o usuário
        User.objects.create_user(email='login@example.com', password='loginpassword123')
        
        url = reverse('token_obtain_pair')
        data = {
            'email': 'login@example.com',
            'password': 'loginpassword123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_invalid_credentials(self):
        """
        Garante que credenciais inválidas retornam erro.
        """
        url = reverse('token_obtain_pair')
        data = {
            'email': 'wrong@example.com',
            'password': 'wrongpassword'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)