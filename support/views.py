from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import ResolveCase
from .serializers import ResolveCaseSerializer
from .selectors import case_selectors
from .services import case_services

class ResolveCaseViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestão de casos de suporte.
    """
    serializer_class = ResolveCaseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return ResolveCase.objects.none()
        return case_selectors.case_list_for_user(user=self.request.user)

    def perform_create(self, serializer):
        case_services.case_create(
            user=self.request.user,
            **serializer.validated_data
        )

    def perform_update(self, serializer):
        case_services.case_update(
            case=self.get_object(),
            **serializer.validated_data
        )
