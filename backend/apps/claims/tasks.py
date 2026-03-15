import time
import logging
from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def process_claim(self, claim_id: int):
    """
    Background task that simulates:
    1. Extracting invoice data
    2. Validating coverage period
    3. Transitioning claim to IN_REVIEW if valid, REJECTED if not
    """
    from .models import Claim, ClaimStatus

    try:
        claim = Claim.objects.select_related('pet').get(pk=claim_id)
    except Claim.DoesNotExist:
        logger.error(f'Claim {claim_id} not found.')
        return

    logger.info(f'[Task] Processing claim {claim_id} for pet "{claim.pet.name}"')

    # Simulate: extracting invoice data (e.g., OCR)
    time.sleep(2)
    logger.info(f'[Task] Invoice data extracted for claim {claim_id}')

    # Validate: date_of_event must fall within pet coverage period
    pet = claim.pet
    is_valid = pet.is_covered_on(claim.date_of_event)

    if is_valid:
        claim.status = ClaimStatus.IN_REVIEW
        claim.review_notes = 'Coverage validated. Awaiting support review.'
        logger.info(f'[Task] Claim {claim_id} is valid → IN_REVIEW')
    else:
        claim.status = ClaimStatus.REJECTED
        claim.review_notes = (
            f'Date of event ({claim.date_of_event}) falls outside '
            f'coverage period ({pet.coverage_start} – {pet.coverage_end}).'
        )
        logger.info(f'[Task] Claim {claim_id} is invalid → REJECTED')

    claim.save(update_fields=['status', 'review_notes', 'updated_at'])
    return {'claim_id': claim_id, 'status': claim.status}
