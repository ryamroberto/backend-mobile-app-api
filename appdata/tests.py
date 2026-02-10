from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from .models import Resource

User = get_user_model()

class ResourceTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='resourcetest@example.com',
            password='testpassword123'
        )
        self.other_user = User.objects.create_user(
            email='other@example.com',
            password='otherpassword123'
        )
        
        url = reverse('token_obtain_pair')
        response = self.client.post(url, {
            'email': 'resourcetest@example.com',
            'password': 'testpassword123'
        }, format='json')
        self.access_token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

    def test_create_resource(self):
        """
        Garante que podemos criar um novo recurso.
        """
        url = reverse('resource-list')
        data = {
            'title': 'Meu Recurso',
            'description': 'Uma descrição de teste',
            'metadata': {'key': 'value'}
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Resource.objects.count(), 1)
        self.assertEqual(Resource.objects.get().owner, self.user)

    def test_list_resources(self):
        """
        Garante que só vemos nossos próprios recursos.
        """
        Resource.objects.create(owner=self.user, title="Meu Recurso")
        Resource.objects.create(owner=self.other_user, title="Recurso Alheio")
        
        url = reverse('resource-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results'] if 'results' in response.data else response.data), 1)
        self.assertEqual(response.data['results'][0]['title'] if 'results' in response.data else response.data[0]['title'], 'Meu Recurso')

    def test_access_other_resource(self):
        """
        Garante que não podemos acessar recursos de outros usuários.
        """
        other_resource = Resource.objects.create(owner=self.other_user, title="Recurso Alheio")
        
        url = reverse('resource-detail', kwargs={'pk': other_resource.id})
        response = self.client.get(url)
        # O DRF retorna 404 se o objeto não estiver no queryset filtrado
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_resource(self):
        """
        Garante que podemos atualizar nosso próprio recurso.
        """
        resource = Resource.objects.create(owner=self.user, title="Antigo Título")
        
        url = reverse('resource-detail', kwargs={'pk': resource.id})
        data = {'title': 'Novo Título'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        resource.refresh_from_db()
        self.assertEqual(resource.title, 'Novo Título')

    def test_delete_resource(self):
        """
        Garante que podemos deletar nosso próprio recurso.
        """
        resource = Resource.objects.create(owner=self.user, title="Para Deletar")
        
        url = reverse('resource-detail', kwargs={'pk': resource.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Resource.objects.count(), 0)