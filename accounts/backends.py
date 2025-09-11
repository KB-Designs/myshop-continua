from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User

class EmailOrUsernameModelBackend(ModelBackend):
    """
    Custom authentication backend that lets users log in with either
    their username or email address.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Try to find the user by username OR email
            user = User.objects.get(username=username) if User.objects.filter(username=username).exists() else User.objects.get(email=username)
        except User.DoesNotExist:
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
