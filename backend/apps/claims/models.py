import hashlib
from django.db import models
from apps.users.models import User
from apps.pets.models import Pet
from .constants import ClaimModelChoices


class Claim(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='claims')
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name='claims')
    invoice = models.FileField(upload_to='invoices/')
    invoice_hash = models.CharField(max_length=64, unique=True, editable=False)
    invoice_date = models.DateField()
    date_of_event = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=ClaimModelChoices.STATUS_CHOICES,
        default=ClaimModelChoices.STATUS_CHOICES.SUBMITTED
    )
    review_notes = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'claims'
        ordering = ('-created_at',)

    def __str__(self):
        return f'Claim #{self.pk} - {self.pet.name} ({self.status})'

    def compute_invoice_hash(self):
        """Compute SHA-256 hash of the invoice file to detect duplicates."""
        self.invoice.seek(0)
        sha256 = hashlib.sha256()
        for chunk in iter(lambda: self.invoice.read(8192), b''):
            sha256.update(chunk)
        self.invoice.seek(0)
        return sha256.hexdigest()
