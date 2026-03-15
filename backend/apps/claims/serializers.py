from rest_framework import serializers
from .models import Claim
from .constants import ClaimModelChoices
from apps.pets.models import Pet
from apps.pets.serializers import PetReadSerializer


class ClaimCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Claim
        fields = ('id', 'pet', 'invoice', 'invoice_date', 'date_of_event', 'amount', 'status')
        read_only_fields = ('id', 'status')

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
        from .tasks import process_claim

        claim = Claim(**validated_data)
        claim.owner = self.context['request'].user

        # Compute hash before saving to catch duplicates
        claim.invoice_hash = claim.compute_invoice_hash()

        # Validate duplicate invoice
        if Claim.objects.filter(invoice_hash=claim.invoice_hash).exists():
            raise serializers.ValidationError(
                {'invoice': 'This invoice has already been submitted.'}
            )

        # Transition to PROCESSING immediately
        claim.status = ClaimModelChoices.STATUS_CHOICES.PROCESSING
        claim.save()

        # Dispatch background task
        process_claim.delay(claim.pk)

        return claim


class ClaimReadSerializer(serializers.ModelSerializer):
    pet = PetReadSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Claim
        fields = (
            'id', 'pet', 'invoice', 'invoice_date', 'date_of_event',
            'amount', 'status', 'status_display', 'review_notes', 'created_at', 'updated_at'
        )
        read_only_fields = fields


class ClaimReviewSerializer(serializers.ModelSerializer):
    """Used by SUPPORT/ADMIN to approve or reject a claim."""

    class Meta:
        model = Claim
        fields = ('status', 'review_notes')

    def validate_status(self, value):
        allowed = (ClaimModelChoices.STATUS_CHOICES.APPROVED, ClaimModelChoices.STATUS_CHOICES.REJECTED)
        if value not in allowed:
            raise serializers.ValidationError(
                f'Support can only set status to: {", ".join(allowed)}'
            )
        return value

    def validate(self, attrs):
        instance = self.instance
        if instance.status != ClaimModelChoices.STATUS_CHOICES.IN_REVIEW:
            raise serializers.ValidationError(
                'Only claims with status IN_REVIEW can be approved or rejected.'
            )
        return attrs
