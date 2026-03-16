from datetime import date, timedelta
from decimal import Decimal

from rest_framework import status
from model_bakery import baker

from apps.users.constants import UserModelChoices
from apps.pets.constants import PetModelChoices
from apps.claims.constants import ClaimModelChoices
from .conftest import make_invoice


class TestPetModel:
    def test_coverage_end_is_365_days_after_start(self, db):
        start = date(2024, 1, 1)
        pet = baker.make(
            'pets.Pet',
            species=PetModelChoices.SPECIES_CHOICES.CAT,
            birth_date=date(2022, 1, 1),
            coverage_start=start,
        )
        assert pet.coverage_end == start + timedelta(days=365)

    def test_is_covered_on(self, db):
        start = date(2024, 1, 1)
        pet = baker.make(
            'pets.Pet',
            species=PetModelChoices.SPECIES_CHOICES.DOG,
            birth_date=date(2020, 1, 1),
            coverage_start=start,
        )
        assert pet.is_covered_on(start) is True
        assert pet.is_covered_on(start + timedelta(days=200)) is True
        assert pet.is_covered_on(start - timedelta(days=1)) is False
        assert pet.is_covered_on(start + timedelta(days=366)) is False


class TestClaimAPI:
    def test_customer_can_create_claim(self, api_client, customer, active_pet, today, mocker):
        mocker.patch('apps.claims.tasks.process_claim.delay')
        api_client.force_authenticate(user=customer)
        data = {
            'pet': active_pet.pk,
            'invoice': make_invoice(),
            'invoice_date': str(today - timedelta(days=10)),
            'date_of_event': str(today - timedelta(days=10)),
            'amount': '250.00',
        }
        response = api_client.post('/api/claims/', data, format='multipart')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['status'] == ClaimModelChoices.STATUS_CHOICES.PROCESSING
        from apps.claims.tasks import process_claim
        process_claim.delay.assert_called_once()

    def test_claim_rejected_if_invoice_date_out_of_coverage(self, api_client, customer, active_pet, today, mocker):
        mock_task = mocker.patch('apps.claims.tasks.process_claim.delay')
        api_client.force_authenticate(user=customer)
        data = {
            'pet': active_pet.pk,
            'invoice': make_invoice(),
            'invoice_date': str(today - timedelta(days=365)),
            'date_of_event': str(today - timedelta(days=365)),
            'amount': '100.00',
        }
        response = api_client.post('/api/claims/', data, format='multipart')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        mock_task.assert_not_called()

    def test_duplicate_invoice_rejected(self, api_client, customer, active_pet, today, mocker):
        mocker.patch('apps.claims.tasks.process_claim.delay')
        api_client.force_authenticate(user=customer)
        content = b'unique invoice content'
        data = {
            'pet': active_pet.pk,
            'invoice': make_invoice(content),
            'invoice_date': str(today - timedelta(days=5)),
            'date_of_event': str(today - timedelta(days=5)),
            'amount': '100.00',
        }
        api_client.post('/api/claims/', data, format='multipart')
        data['invoice'] = make_invoice(content)
        response = api_client.post('/api/claims/', data, format='multipart')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_support_can_review_claim(self, api_client, customer, support, active_pet, today):
        claim = baker.make(
            'claims.Claim',
            owner=customer,
            pet=active_pet,
            invoice=make_invoice(),
            invoice_hash='abc123unique',
            invoice_date=today - timedelta(days=5),
            date_of_event=today - timedelta(days=5),
            amount=Decimal('100.00'),
            status=ClaimModelChoices.STATUS_CHOICES.IN_REVIEW,
        )
        api_client.force_authenticate(user=support)
        response = api_client.patch(
            f'/api/claims/{claim.pk}/review/',
            {'status': 'APPROVED', 'review_notes': 'All good'},
            format='json',
        )
        assert response.status_code == status.HTTP_200_OK
        claim.refresh_from_db()
        assert claim.status == ClaimModelChoices.STATUS_CHOICES.APPROVED

    def test_customer_cannot_review_claim(self, api_client, customer, active_pet, today):
        claim = baker.make(
            'claims.Claim',
            owner=customer,
            pet=active_pet,
            invoice=make_invoice(),
            invoice_hash='xyz789unique',
            invoice_date=today - timedelta(days=5),
            date_of_event=today - timedelta(days=5),
            amount=Decimal('100.00'),
            status=ClaimModelChoices.STATUS_CHOICES.IN_REVIEW,
        )
        api_client.force_authenticate(user=customer)
        response = api_client.patch(
            f'/api/claims/{claim.pk}/review/',
            {'status': 'APPROVED'},
            format='json',
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_support_cannot_review_non_in_review_claim(self, api_client, customer, support, active_pet, today):
        claim = baker.make(
            'claims.Claim',
            owner=customer,
            pet=active_pet,
            invoice=make_invoice(),
            invoice_hash='hash456unique',
            invoice_date=today - timedelta(days=5),
            date_of_event=today - timedelta(days=5),
            amount=Decimal('100.00'),
            status=ClaimModelChoices.STATUS_CHOICES.PROCESSING,
        )
        api_client.force_authenticate(user=support)
        response = api_client.patch(
            f'/api/claims/{claim.pk}/review/',
            {'status': 'APPROVED'},
            format='json',
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_customer_only_sees_own_claims(self, api_client, customer, today):
        other_user = baker.make(
            'users.User',
            email='other@test.com',
            role=UserModelChoices.ROLE_CHOICES.CUSTOMER,
            is_active=True,
        )
        other_pet = baker.make(
            'pets.Pet',
            owner=other_user,
            species=PetModelChoices.SPECIES_CHOICES.CAT,
            birth_date=date(2020, 1, 1),
            coverage_start=today - timedelta(days=10),
        )
        baker.make(
            'claims.Claim',
            owner=other_user,
            pet=other_pet,
            invoice=make_invoice(),
            invoice_hash='other_hash',
            invoice_date=today - timedelta(days=5),
            date_of_event=today - timedelta(days=5),
            amount=Decimal('50.00'),
        )
        api_client.force_authenticate(user=customer)
        response = api_client.get('/api/claims/')
        assert response.status_code == status.HTTP_200_OK
        for claim in response.data:
            assert claim.get('owner') != other_user.pk
