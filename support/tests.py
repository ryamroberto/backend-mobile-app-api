from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from .models import ResolveCase

User = get_user_model()

class SupportTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='user@example.com',
            password='password123'
        )
        self.staff_user = User.objects.create_user(
            email='staff@example.com',
            password='password123',
            is_staff=True
        )
        self.other_user = User.objects.create_user(
            email='other@example.com',
            password='password123'
        )
        
        # Token para usuário comum
        url = reverse('token_obtain_pair')
        response = self.client.post(url, {'email': 'user@example.com', 'password': 'password123'})
        self.user_token = response.data['access']
        
        # Token para staff
        response = self.client.post(url, {'email': 'staff@example.com', 'password': 'password123'})
        self.staff_token = response.data['access']

    def test_create_case(self):
        """Garante que um usuário pode criar um caso de suporte."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
        url = reverse('cases-list')
        data = {
            'title': 'Problema técnico',
            'description': 'Não consigo acessar o módulo de IA.',
            'category': 'TECHNICAL'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ResolveCase.objects.count(), 1)
        self.assertEqual(ResolveCase.objects.get().requester, self.user)

    def test_list_own_cases(self):
        """Garante que o usuário vê apenas seus próprios casos."""
        ResolveCase.objects.create(requester=self.user, title="Meu caso")
        ResolveCase.objects.create(requester=self.other_user, title="Caso alheio")
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
        url = reverse('cases-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Verifica se retornou apenas 1 caso (o dele)
        results = response.data['results'] if 'results' in response.data else response.data
        self.assertEqual(len(results), 1)

    def test_staff_list_all_cases(self):
        """Garante que o staff vê todos os casos."""
        ResolveCase.objects.create(requester=self.user, title="Caso 1")
        ResolveCase.objects.create(requester=self.other_user, title="Caso 2")
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.staff_token}')
        url = reverse('cases-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results'] if 'results' in response.data else response.data
        self.assertEqual(len(results), 2)

    def test_user_cannot_access_other_case(self):
        """Garante que um usuário não pode acessar detalhe de caso de outro."""
        other_case = ResolveCase.objects.create(requester=self.other_user, title="Caso alheio")
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user_token}')
        url = reverse('cases-detail', kwargs={'pk': other_case.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
