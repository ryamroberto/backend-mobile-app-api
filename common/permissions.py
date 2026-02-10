from rest_framework import permissions

class IsOwner(permissions.BasePermission):
    """
    Permissão personalizada para permitir apenas que os proprietários de um objeto o editem ou visualizem.
    """
    def has_object_permission(self, request, view, obj):
        # As permissões de leitura são permitidas para o proprietário.
        # As permissões de escrita também são permitidas apenas para o proprietário.
        return obj.owner == request.user
