import io
from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import patch

from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from rest_framework import status

from apps.users.models import User, UserRole
from apps.pets.models import Pet
from apps.claims.models import Claim
from apps.claims.constants import ClaimModelChoices


def make_invoice(content=b'invoice content'):
    return SimpleUploadedFile('invoice.pdf', content, content_type='application/pdf')


class BaseTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.customer = User.objects.create_user(
            email='customer@test.com', password='pass1234', role=UserRole.CUSTOMER
        )
        self.support = User.objects.create_user(
            email='support@test.com', password='pass1234', role=UserRole.SUPPORT
        )
        self.today = date.today()
        self.pet = Pet.objects.create(
            owner=self.customer,
            name='Rex',
            species='DOG',
            birth_date=date(2020, 1, 1),
            coverage_start=self.today - timedelta(days=30),
        )

    def authenticate(self, user):
        self.client.force_authenticate(user=user)


class PetModelTest(TestCase):
    def test_coverage_end_is_365_days_after_start(self):
        start = date(2024, 1, 1)
        pet = Pet(
            owner=User.objects.create_user(email='u@t.com', password='pw'),
            name='Cat',
            species='CAT',
            birth_date=date(2022, 1, 1),
            coverage_start=start,
        )
        pet.save()
        self.assertEqual(pet.coverage_end, start + timedelta(days=365))

    def test_is_covered_on(self):
        start = date(2024, 1, 1)
        user = User.objects.create_user(email='u2@t.com', password='pw')
        pet = Pet.objects.create(
            owner=user, name='Dog', species='DOG',
            birth_date=date(2020, 1, 1), coverage_start=start
        )
        self.assertTrue(pet.is_covered_on(start))
        self.assertTrue(pet.is_covered_on(start + timedelta(days=200)))
        self.assertFalse(pet.is_covered_on(start - timedelta(days=1)))
        self.assertFalse(pet.is_covered_on(start + timedelta(days=366)))


class ClaimAPITest(BaseTestCase):
    @patch('apps.claims.tasks.process_claim.delay')
    def test_customer_can_create_claim(self, mock_task):
        self.authenticate(self.customer)
        data = {
            'pet': self.pet.pk,
            'invoice': make_invoice(),
            'invoice_date': str(self.today - timedelta(days=10)),
            'date_of_event': str(self.today - timedelta(days=10)),
            'amount': '250.00',
        }
        response = self.client.post('/api/claims/', data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], ClaimModelChoices.STATUS_CHOICES.PROCESSING)
        mock_task.assert_called_once()

    @patch('apps.claims.tasks.process_claim.delay')
    def test_claim_rejected_if_invoice_date_out_of_coverage(self, mock_task):
        self.authenticate(self.customer)
        data = {
            'pet': self.pet.pk,
            'invoice': make_invoice(),
            'invoice_date': str(self.today - timedelta(days=365)),
            'date_of_event': str(self.today - timedelta(days=365)),
            'amount': '100.00',
        }
        response = self.client.post('/api/claims/', data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        mock_task.assert_not_called()

    @patch('apps.claims.tasks.process_claim.delay')
    def test_duplicate_invoice_rejected(self, mock_task):
        self.authenticate(self.customer)
        content = b'unique invoice content'
        data = {
            'pet': self.pet.pk,
            'invoice': make_invoice(content),
            'invoice_date': str(self.today - timedelta(days=5)),
            'date_of_event': str(self.today - timedelta(days=5)),
            'amount': '100.00',
        }
        self.client.post('/api/claims/', data, format='multipart')
        data['invoice'] = make_invoice(content)
        response = self.client.post('/api/claims/', data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_support_can_review_claim(self):
        claim = Claim.objects.create(
            owner=self.customer,
            pet=self.pet,
            invoice=make_invoice(),
            invoice_hash='abc123unique',
            invoice_date=self.today - timedelta(days=5),
            date_of_event=self.today - timedelta(days=5),
            amount=Decimal('100.00'),
            status=ClaimModelChoices.STATUS_CHOICES.IN_REVIEW,
        )
        self.authenticate(self.support)
        response = self.client.patch(
            f'/api/claims/{claim.pk}/review/',
            {'status': 'APPROVED', 'review_notes': 'All good'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        claim.refresh_from_db()
        self.assertEqual(claim.status, ClaimModelChoices.STATUS_CHOICES.APPROVED)

    def test_customer_cannot_review_claim(self):
        claim = Claim.objects.create(
            owner=self.customer,
            pet=self.pet,
            invoice=make_invoice(),
            invoice_hash='xyz789unique',
            invoice_date=self.today - timedelta(days=5),
            date_of_event=self.today - timedelta(days=5),
            amount=Decimal('100.00'),
            status=ClaimModelChoices.STATUS_CHOICES.IN_REVIEW,
        )
        self.authenticate(self.customer)
        response = self.client.patch(
            f'/api/claims/{claim.pk}/review/',
            {'status': 'APPROVED'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_support_cannot_review_non_in_review_claim(self):
        claim = Claim.objects.create(
            owner=self.customer,
            pet=self.pet,
            invoice=make_invoice(),
            invoice_hash='hash456unique',
            invoice_date=self.today - timedelta(days=5),
            date_of_event=self.today - timedelta(days=5),
            amount=Decimal('100.00'),
            status=ClaimModelChoices.STATUS_CHOICES.PROCESSING,
        )
        self.authenticate(self.support)
        response = self.client.patch(
            f'/api/claims/{claim.pk}/review/',
            {'status': 'APPROVED'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_customer_only_sees_own_claims(self):
        other_user = User.objects.create_user(email='other@test.com', password='pw')
        other_pet = Pet.objects.create(
            owner=other_user, name='Cat', species='CAT',
            birth_date=date(2020, 1, 1), coverage_start=self.today - timedelta(days=10)
        )
        Claim.objects.create(
            owner=other_user, pet=other_pet,
            invoice=make_invoice(), invoice_hash='other_hash',
            invoice_date=self.today - timedelta(days=5),
            date_of_event=self.today - timedelta(days=5),
            amount=Decimal('50.00'),
        )
        self.authenticate(self.customer)
        response = self.client.get('/api/claims/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for claim in response.data:
            self.assertNotEqual(claim.get('owner'), other_user.pk)
