from rest_framework import generics, status, views
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.throttling import AnonRateThrottle
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import RegisterSerializer

from django.conf import settings

class AuthThrottle(AnonRateThrottle):
    scope = 'auth'

    def allow_request(self, request, view):
        # Permite desabilitar throttling em testes, a menos que explicitamente solicitado
        if getattr(settings, 'DISABLE_THROTTLING', False):
            return True
        return super().allow_request(request, view)

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
    throttle_classes = [AuthThrottle]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response({
                "mensagem": "Usuário registrado com sucesso."
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(TokenObtainPairView):
    throttle_classes = [AuthThrottle]

class LogoutView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({
                "mensagem": "Logout realizado com sucesso."
            }, status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            return Response({
                "erro": "Token inválido ou não fornecido."
            }, status=status.HTTP_400_BAD_REQUEST)