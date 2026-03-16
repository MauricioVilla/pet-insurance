import logging
from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task
def activate_approved_pets():
    """Transition pets from APPROVED to ACTIVE when coverage_start <= today."""
    from .models import Pet
    from .constants import PetModelChoices

    today = timezone.now().date()
    pets = Pet.objects.filter(
        status=PetModelChoices.STATUS_CHOICES.APPROVED,
        coverage_start__lte=today,
    )
    count = pets.update(status=PetModelChoices.STATUS_CHOICES.ACTIVE)
    if count:
        logger.info(f'[Task] Activated {count} pet(s) with coverage starting on or before {today}.')
    return count
