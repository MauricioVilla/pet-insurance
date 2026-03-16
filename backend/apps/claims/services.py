from rest_framework.exceptions import ValidationError

from apps.core.services import BaseService
from apps.users.constants import UserModelChoices
from .constants import ClaimModelChoices
from .models import Claim


class ClaimService(BaseService):
    model = Claim
    serializer_class = None

    def get_queryset(self, user):
        qs = Claim.objects.select_related('pet', 'owner')
        if user.role in (UserModelChoices.ROLE_CHOICES.ADMIN, UserModelChoices.ROLE_CHOICES.SUPPORT):
            return qs.all()
        return qs.filter(owner=user)

    def create_claim(self, validated_data, user):
        from .tasks import process_claim

        claim = Claim(**validated_data)
        claim.owner = user
        claim.invoice_hash = claim.compute_invoice_hash()

        if Claim.objects.filter(invoice_hash=claim.invoice_hash).exists():
            raise ValidationError({'invoice': 'This invoice has already been submitted.'})

        claim.status = ClaimModelChoices.STATUS_CHOICES.PROCESSING
        claim.save()

        process_claim.delay(claim.pk)
        return claim

    def validate_pet_ownership(self, pet, user):
        if pet.owner != user:
            raise ValidationError({'pet': 'You do not own this pet.'})
        if pet.status != 'ACTIVE':
            raise ValidationError({'pet': 'This pet does not have active coverage.'})

    def validate_coverage(self, pet, invoice_date):
        if not pet.is_covered_on(invoice_date):
            raise ValidationError({
                'invoice_date': (
                    f'Invoice date {invoice_date} is outside the pet\'s coverage period '
                    f'({pet.coverage_start} – {pet.coverage_end}).'
                )
            })

    def review_claim(self, claim, status, review_notes=''):
        if claim.status != ClaimModelChoices.STATUS_CHOICES.IN_REVIEW:
            raise ValidationError(
                'Only claims with status IN_REVIEW can be approved or rejected.'
            )

        allowed = (ClaimModelChoices.STATUS_CHOICES.APPROVED, ClaimModelChoices.STATUS_CHOICES.REJECTED)
        if status not in allowed:
            raise ValidationError(
                {'status': f'Support can only set status to: {", ".join(allowed)}'}
            )

        claim.status = status
        claim.review_notes = review_notes
        claim.save(update_fields=['status', 'review_notes', 'updated_at'])
        return claim
