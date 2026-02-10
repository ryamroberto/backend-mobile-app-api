from rest_framework import serializers
from .models import Resource

class ResourceSerializer(serializers.ModelSerializer):
    owner_email = serializers.EmailField(source='owner.email', read_only=True)

    class Meta:
        model = Resource
        fields = ('id', 'owner_email', 'title', 'description', 'status', 'metadata', 'created_at', 'updated_at')
        read_only_fields = ('id', 'owner_email', 'created_at', 'updated_at')
