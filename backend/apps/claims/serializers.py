from rest_framework import serializers
from .models import Claim, ClaimStatus
from apps.pets.models import Pet
from apps.pets.serializers import PetReadSerializer


class ClaimCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Claim
        fields = ('pet', 'invoice', 'invoice_date', 'date_of_event', 'amount')

    def validate_pet(self, pet):
        user = self.context['request'].user
        if pet.owner != user:
            raise serializers.ValidationError('You do not own this pet.')
        return pet

    def validate(self, attrs):
        pet = attrs['pet']
        invoice_date = attrs['invoice_date']

        # Business Rule: invoice_date must be within coverage period
        if not pet.is_covered_on(invoice_date):
            raise serializers.ValidationError({
                'invoice_date': (
                    f'Invoice date {invoice_date} is outside the pet\'s coverage period '
                    f'({pet.coverage_start} – {pet.coverage_end}).'
                )
            })
        return attrs

    def create(self, validated_data):
        invoice_file = validated_data.get('invoice')
        claim = Claim(**validated_data)
        claim.owner = self.context['request'].user

        # Compute hash before saving to catch duplicates
        claim.invoice_hash = claim.compute_invoice_hash()

        claim.save()

        return claim


class ClaimReadSerializer(serializers.ModelSerializer):
    pet = PetReadSerializer(read_only=True)

    class Meta:
        model = Claim
        fields = (
            'id', 'pet', 'invoice', 'invoice_date', 'date_of_event',
            'amount', 'status', 'review_notes', 'created_at', 'updated_at'
        )
        read_only_fields = fields


class ClaimReviewSerializer(serializers.ModelSerializer):
    """Used by SUPPORT/ADMIN to approve or reject a claim."""

    class Meta:
        model = Claim
        fields = ('status', 'review_notes')

    def validate_status(self, value):
        allowed = (ClaimStatus.APPROVED, ClaimStatus.REJECTED)
        if value not in allowed:
            raise serializers.ValidationError(
                f'Support can only set status to: {", ".join(allowed)}'
            )
        return value

    def validate(self, attrs):
        instance = self.instance
        if instance.status != ClaimStatus.IN_REVIEW:
            raise serializers.ValidationError(
                'Only claims with status IN_REVIEW can be approved or rejected.'
            )
        return attrs
