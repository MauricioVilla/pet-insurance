from rest_framework import viewsets, permissions, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from apps.users.models import UserRole
from .models import Claim, ClaimStatus
from .serializers import ClaimCreateSerializer, ClaimReadSerializer, ClaimReviewSerializer
from .filters import ClaimFilter


@extend_schema_view(
    list=extend_schema(summary='List claims'),
    create=extend_schema(summary='Submit a new reimbursement claim'),
    retrieve=extend_schema(summary='Get claim details'),
)
class ClaimViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = (permissions.IsAuthenticated,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = ClaimFilter

    def get_queryset(self):
        user = self.request.user
        qs = Claim.objects.select_related('pet', 'owner')
        if user.role in (UserRole.ADMIN, UserRole.SUPPORT):
            return qs.all()
        return qs.filter(owner=user)

    def get_serializer_class(self):
        if self.action == 'create':
            return ClaimCreateSerializer
        if self.action == 'review':
            return ClaimReviewSerializer
        return ClaimReadSerializer

    def get_permissions(self):
        if self.action == 'review':
            from apps.pets.permissions import IsSupportOrAdmin
            return [permissions.IsAuthenticated(), IsSupportOrAdmin()]
        return super().get_permissions()

    @extend_schema(
        summary='Approve or reject a claim (Support/Admin only)',
        request=ClaimReviewSerializer,
        responses={200: ClaimReadSerializer},
    )
    @action(detail=True, methods=['patch'], url_path='review')
    def review(self, request, pk=None):
        claim = self.get_object()
        serializer = ClaimReviewSerializer(claim, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(ClaimReadSerializer(claim).data)
