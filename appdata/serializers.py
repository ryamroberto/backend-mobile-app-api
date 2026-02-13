from rest_framework import serializers
from .models import AutomationTask

class AutomationTaskSerializer(serializers.ModelSerializer):
    owner_email = serializers.EmailField(source='owner.email', read_only=True)
    task_type_display = serializers.CharField(source='get_task_type_display', read_only=True)
    execution_status_display = serializers.CharField(source='get_execution_status_display', read_only=True)

    class Meta:
        model = AutomationTask
        fields = (
            'id', 'owner_email', 'title', 'description', 
            'task_type', 'task_type_display', 
            'provider_id', 'execution_status', 'execution_status_display',
            'input_params', 'output_results', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'owner_email', 'created_at', 'updated_at')

    def validate(self, data):
        """
        Validação customizada para garantir provider_id se não for CUSTOM.
        """
        task_type = data.get('task_type', AutomationTask.TaskType.CUSTOM)
        provider_id = data.get('provider_id')

        if task_type != AutomationTask.TaskType.CUSTOM and not provider_id:
            raise serializers.ValidationError({
                'provider_id': 'O ID do provedor é obrigatório para tarefas que não sejam CUSTOM.'
            })
        return data
