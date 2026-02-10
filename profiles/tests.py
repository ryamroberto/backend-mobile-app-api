from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from profiles.models import Profile

User = get_user_model()

class ProfileTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='profiletest@example.com',
            password='testpassword123'
        )
        url = reverse('token_obtain_pair')
        response = self.client.post(url, {
            'email': 'profiletest@example.com',
            'password': 'testpassword123'
        }, format='json')
        self.access_token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

    def test_profile_created_automatically(self):
        """
        Garante que um perfil é criado automaticamente quando um usuário é criado.
        """
        self.assertTrue(Profile.objects.filter(user=self.user).exists())
        self.assertEqual(self.user.profile.full_name, '')

    def test_get_my_profile(self):
        """
        Garante que o usuário pode visualizar seu próprio perfil.
        """
        url = reverse('profile-me')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'profiletest@example.com')

    def test_update_my_profile(self):
        """
        Garante que o usuário pode atualizar seu próprio perfil.
        """
        url = reverse('profile-me')
        data = {
            'full_name': 'João Silva',
            'bio': 'Desenvolvedor Django'
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.full_name, 'João Silva')
        self.assertEqual(self.user.profile.bio, 'Desenvolvedor Django')

    def test_profile_unauthenticated(self):
        """
        Garante que usuários não autenticados não podem acessar o perfil.
        """
        self.client.credentials() # Limpa credenciais
        url = reverse('profile-me')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)