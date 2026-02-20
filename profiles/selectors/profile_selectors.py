from ..models import Profile
from users.models import User

def profile_get_for_user(*, user: User) -> Profile:
    """
    Retorna o perfil associado a um usuário.
    """
    return user.profile
