from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Profile
from .serializers import ProfileSerializer

class ProfileMeView(generics.RetrieveUpdateAPIView):

    serializer_class = ProfileSerializer

    permission_classes = [IsAuthenticated]



    def get_object(self):

        if getattr(self, 'swagger_fake_view', False):

            return None

        return self.request.user.profile
