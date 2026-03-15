from rest_framework import viewsets, permissions
from drf_spectacular.utils import extend_schema, extend_schema_view
from .models import Pet
from .serializers import PetSerializer
from .permissions import IsOwnerOrAdminOrSupport


@extend_schema_view(
    list=extend_schema(summary='List all pets for current user'),
    create=extend_schema(summary='Register a new pet'),
    retrieve=extend_schema(summary='Get pet details'),
    update=extend_schema(summary='Update pet'),
    destroy=extend_schema(summary='Delete pet'),
)
class PetViewSet(viewsets.ModelViewSet):
    serializer_class = PetSerializer
    permission_classes = (permissions.IsAuthenticated, IsOwnerOrAdminOrSupport)

    def get_queryset(self):
        user = self.request.user
        from apps.users.models import UserRole
        if user.role in (UserRole.ADMIN, UserRole.SUPPORT):
            return Pet.objects.all().select_related('owner')
        return Pet.objects.filter(owner=user).select_related('owner')
