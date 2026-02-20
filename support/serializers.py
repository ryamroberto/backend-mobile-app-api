from rest_framework import serializers
from .models import ResolveCase

class ResolveCaseSerializer(serializers.ModelSerializer):
    requester_email = serializers.EmailField(source='requester.email', read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = ResolveCase
        fields = (
            'id', 'requester_email', 'title', 'description',
            'category', 'category_display', 'status', 'status_display',
            'resolution_notes', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'requester_email', 'created_at', 'updated_at')
