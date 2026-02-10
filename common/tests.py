from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

class DocumentationTests(APITestCase):
    def test_swagger_ui_accessible(self):
        """
        Garante que a interface do Swagger UI está acessível.
        """
        url = reverse('schema-swagger-ui')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_redoc_ui_accessible(self):
        """
        Garante que a interface do ReDoc está acessível.
        """
        url = reverse('schema-redoc')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_swagger_json_accessible(self):
        """
        Garante que o arquivo swagger.json está sendo gerado.
        """
        url = reverse('schema-json', kwargs={'format': '.json'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)