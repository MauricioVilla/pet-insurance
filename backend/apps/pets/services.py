from datetime import datetime

from rest_framework.exceptions import ValidationError

from apps.core.services import BaseService
from apps.users.constants import UserModelChoices
from .constants import PetModelChoices
from .models import Pet
from .api.serializers import PetSerializer, PetReadSerializer


class PetService(BaseService):
    model = Pet
    serializer_class = PetReadSerializer

    def get_queryset(self, user):
        if user.role in (UserModelChoices.ROLE_CHOICES.ADMIN, UserModelChoices.ROLE_CHOICES.SUPPORT):
            return Pet.objects.all().select_related('owner')
        return Pet.objects.filter(owner=user).select_related('owner')

    def activate(self, pet, coverage_start=None):
        if pet.status == PetModelChoices.STATUS_CHOICES.ACTIVE:
            raise ValidationError({'detail': 'Pet coverage is already active.'})

        if coverage_start and isinstance(coverage_start, str):
            try:
                coverage_start = datetime.strptime(coverage_start, '%Y-%m-%d').date()
            except ValueError:
                raise ValidationError({'coverage_start': 'Invalid date format. Use YYYY-MM-DD.'})

        pet.activate(coverage_start=coverage_start)
        return pet
