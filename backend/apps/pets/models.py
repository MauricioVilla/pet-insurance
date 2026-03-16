from django.db import models
from django.utils import timezone
from datetime import timedelta
from apps.users.models import User
from .constants import PetModelChoices


class Pet(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pets')
    name = models.CharField(max_length=100)
    species = models.CharField(max_length=10, choices=PetModelChoices.SPECIES_CHOICES)
    birth_date = models.DateField()
    status = models.CharField(max_length=10, choices=PetModelChoices.STATUS_CHOICES, default=PetModelChoices.STATUS_CHOICES.PENDING)
    coverage_start = models.DateField(null=True, blank=True)
    coverage_end = models.DateField(null=True, blank=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'pets'

    def save(self, *args, **kwargs):
        if self.coverage_start:
            self.coverage_end = self.coverage_start + timedelta(days=365)
        else:
            self.coverage_end = None
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.name} ({self.species}) - {self.owner.email}'

    def is_covered_on(self, date):
        """Check if pet had insurance coverage on a given date."""
        if not self.coverage_start or not self.coverage_end:
            return False
        return self.coverage_start <= date <= self.coverage_end

    def activate(self, coverage_start=None):
        """Approve coverage starting on given date (or today). Sets ACTIVE or APPROVED depending on date."""
        self.coverage_start = coverage_start or timezone.now().date()
        if self.coverage_start <= timezone.now().date():
            self.status = PetModelChoices.STATUS_CHOICES.ACTIVE
        else:
            self.status = PetModelChoices.STATUS_CHOICES.APPROVED
        self.save()
