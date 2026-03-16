from rest_framework import serializers
from ..models import Claim
from ..constants import ClaimModelChoices
from ..services import ClaimService
from apps.pets.api.serializers import PetReadSerializer

claim_service = ClaimService()


class ClaimCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Claim
        fields = ('id', 'pet', 'invoice', 'invoice_date', 'date_of_event', 'amount', 'status')
        read_only_fields = ('id', 'status')

    def validate_pet(self, pet):
        user = self.context['request'].user
        claim_service.validate_pet_ownership(pet, user)
        return pet

    def validate(self, attrs):
        claim_service.validate_coverage(attrs['pet'], attrs['invoice_date'])
        return attrs

    def create(self, validated_data):
        user = self.context['request'].user
        return claim_service.create_claim(validated_data, user)


class ClaimReadSerializer(serializers.ModelSerializer):
    pet = PetReadSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    owner_name = serializers.CharField(source='owner.name', read_only=True)
    owner_email = serializers.EmailField(source='owner.email', read_only=True)

    class Meta:
        model = Claim
        fields = (
            'id', 'pet', 'owner_name', 'owner_email', 'invoice', 'invoice_date', 'date_of_event',
            'amount', 'status', 'status_display', 'review_notes', 'created_at', 'updated_at'
        )
        read_only_fields = fields


class ClaimReviewSerializer(serializers.Serializer):
    """Used by SUPPORT/ADMIN to approve or reject a claim. Validation in ClaimService."""
    status = serializers.CharField()
    review_notes = serializers.CharField(required=False, default='')
