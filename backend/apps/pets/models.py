from django.db import models
from django.utils import timezone
from datetime import timedelta
from apps.users.models import User


class Species(models.TextChoices):
    DOG = 'DOG', 'Dog'
    CAT = 'CAT', 'Cat'
    OTHER = 'OTHER', 'Other'


class Pet(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pets')
    name = models.CharField(max_length=100)
    species = models.CharField(max_length=10, choices=Species.choices)
    birth_date = models.DateField()
    coverage_start = models.DateField()
    coverage_end = models.DateField(editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'pets'

    def save(self, *args, **kwargs):
        # Business rule: coverage_end = coverage_start + 365 days
        self.coverage_end = self.coverage_start + timedelta(days=365)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.name} ({self.species}) - {self.owner.email}'

    def is_covered_on(self, date):
        """Check if pet had insurance coverage on a given date."""
        return self.coverage_start <= date <= self.coverage_end
