from typing import Any, Dict
from django.db import transaction
from ..models import Resource
from users.models import User

@transaction.atomic
def resource_create(
    *,
    user: User,
    title: str,
    description: str = "",
    status: str = Resource.Status.ACTIVE,
    metadata: Dict[str, Any] = None
) -> Resource:
    """
    Cria um novo recurso associado a um usuário.
    """
    if metadata is None:
        metadata = {}
        
    resource = Resource(
        owner=user,
        title=title,
        description=description,
        status=status,
        metadata=metadata
    )
    resource.full_clean()
    resource.save()
    
    return resource

@transaction.atomic
def resource_update(
    *,
    resource: Resource,
    **data
) -> Resource:
    """
    Atualiza um recurso existente.
    """
    # Lista de campos permitidos para atualização
    update_fields = ['title', 'description', 'status', 'metadata']
    
    for field in update_fields:
        if field in data:
            setattr(resource, field, data[field])
            
    resource.full_clean()
    resource.save()
    
    return resource

@transaction.atomic
def resource_delete(*, resource: Resource) -> None:
    """
    Remove um recurso.
    """
    resource.delete()
