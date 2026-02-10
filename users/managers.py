from django.contrib.auth.base_user import BaseUserManager

class CustomUserManager(BaseUserManager):
    """
    Gerenciador de modelo de usuário personalizado onde o e-mail é o identificador exclusivo
    para autenticação em vez de nomes de usuário.
    """
    def create_user(self, email, password, **extra_fields):
        """
        Cria e salva um Usuário com o e-mail e a senha fornecidos.
        """
        if not email:
            raise ValueError('O e-mail deve ser definido')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Cria e salva um Superusuário com o e-mail e a senha fornecidos.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser deve ter is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser deve ter is_superuser=True.')
        return self.create_user(email, password, **extra_fields)
