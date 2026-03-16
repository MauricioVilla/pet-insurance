from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, extend_schema_view
from .serializers import PetSerializer, PetReadSerializer
from ..permissions import IsOwnerOrAdminOrSupport, IsSupportOrAdmin
from ..services import PetService

pet_service = PetService()


@extend_schema_view(
    list=extend_schema(summary='List all pets for current user'),
    create=extend_schema(summary='Register a new pet'),
    retrieve=extend_schema(summary='Get pet details'),
    update=extend_schema(summary='Update pet'),
    destroy=extend_schema(summary='Delete pet'),
)
class PetViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated, IsOwnerOrAdminOrSupport)

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return PetReadSerializer
        return PetSerializer

    def get_queryset(self):
        return pet_service.get_queryset(self.request.user)

    @extend_schema(summary='Activate pet coverage (support/admin only)')
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated, IsSupportOrAdmin])
    def activate(self, request, pk=None):
        pet = self.get_object()
        pet = pet_service.activate(pet, coverage_start=request.data.get('coverage_start'))
        return Response(PetReadSerializer(pet).data)
