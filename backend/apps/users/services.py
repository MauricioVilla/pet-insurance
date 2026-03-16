from apps.core.services import BaseService
from .models import User


class UserService(BaseService):
    model = User
    serializer_class = None

    def register(self, validated_data):
        return User.objects.create_user(**validated_data)

    def get_by_email(self, email):
        try:
            return User.objects.get(email=email)
        except User.DoesNotExist:
            return None
