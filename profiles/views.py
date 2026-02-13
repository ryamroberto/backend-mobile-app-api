from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .serializers import ProfileSerializer
from .selectors import profile_selectors
from .services import profile_services

class ProfileMeView(generics.RetrieveUpdateAPIView):
    """
    View para o usuário autenticado visualizar e editar seu próprio perfil.
    """
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """
        Utiliza o selector para obter o perfil do usuário logado.
        """
        if getattr(self, 'swagger_fake_view', False):
            return None
        return profile_selectors.profile_get_for_user(user=self.request.user)

    def perform_update(self, serializer):
        """
        Utiliza o service para atualizar o perfil.
        """
        profile_services.profile_update(
            profile=self.get_object(),
            **serializer.validated_data
        )
