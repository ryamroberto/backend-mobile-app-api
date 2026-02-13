from typing import Any, Dict
from django.db import transaction
from ..models import Profile
from users.models import User

@transaction.atomic
def profile_create(*, user: User) -> Profile:
    """
    Cria um perfil para um usuário.
    """
    profile = Profile(user=user)
    profile.full_clean()
    profile.save()
    return profile

@transaction.atomic
def profile_update(*, profile: Profile, **data) -> Profile:
    """
    Atualiza o perfil de um usuário.
    """
    # Lista de campos permitidos para atualização
    update_fields = ['full_name', 'bio', 'avatar']
    
    for field in update_fields:
        if field in data:
            setattr(profile, field, data[field])
            
    profile.full_clean()
    profile.save()
    
    return profile
