from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from .models import AutomationTask

User = get_user_model()

class AutomationTaskTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='tasktest@example.com',
            password='testpassword123'
        )
        self.other_user = User.objects.create_user(
            email='other_task@example.com',
            password='otherpassword123'
        )
        
        url = reverse('token_obtain_pair')
        response = self.client.post(url, {
            'email': 'tasktest@example.com',
            'password': 'testpassword123'
        }, format='json')
        self.access_token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

    def test_create_task_custom(self):
        """
        Garante que podemos criar uma nova tarefa customizada.
        """
        url = reverse('tasks-list')
        data = {
            'title': 'Minha Automação',
            'task_type': 'CUSTOM',
            'description': 'Teste de automação customizada'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(AutomationTask.objects.count(), 1)
        self.assertEqual(AutomationTask.objects.get().owner, self.user)

    def test_create_task_bedrock_without_provider_id(self):
        """
        Garante que falha ao criar BEDROCK sem provider_id.
        """
        url = reverse('tasks-list')
        data = {
            'title': 'Tarefa Bedrock',
            'task_type': 'BEDROCK'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('provider_id', response.data)

    def test_create_task_bedrock_with_provider_id(self):
        """
        Garante que sucesso ao criar BEDROCK com provider_id.
        """
        url = reverse('tasks-list')
        data = {
            'title': 'Tarefa Bedrock',
            'task_type': 'BEDROCK',
            'provider_id': 'arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-v2'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_list_tasks(self):
        """
        Garante que só vemos nossas próprias tarefas.
        """
        AutomationTask.objects.create(owner=self.user, title="Minha Tarefa")
        AutomationTask.objects.create(owner=self.other_user, title="Tarefa Alheia")
        
        url = reverse('tasks-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        count = len(response.data['results'] if 'results' in response.data else response.data)
        self.assertEqual(count, 1)

    def test_update_task_status(self):
        """
        Garante que podemos atualizar o status de uma tarefa.
        """
        task = AutomationTask.objects.create(owner=self.user, title="Tarefa X")
        url = reverse('tasks-detail', kwargs={'pk': task.id})
        data = {'execution_status': 'RUNNING'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        task.refresh_from_db()
        self.assertEqual(task.execution_status, 'RUNNING')
