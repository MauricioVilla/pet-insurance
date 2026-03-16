import pytest
from datetime import date, timedelta

from rest_framework import status
from model_bakery import baker

from apps.pets.constants import PetModelChoices


class TestApprovePetAPI:
    def test_support_approves_pet_with_today_becomes_active(self, api_client, support, pending_pet, today):
        api_client.force_authenticate(user=support)
        response = api_client.post(
            f'/api/pets/{pending_pet.pk}/activate/',
            {'coverage_start': str(today)},
            format='json',
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == PetModelChoices.STATUS_CHOICES.ACTIVE
        assert response.data['coverage_start'] == str(today)
        assert response.data['coverage_end'] == str(today + timedelta(days=365))

    def test_support_approves_pet_with_past_date_becomes_active(self, api_client, support, pending_pet, today):
        past = today - timedelta(days=10)
        api_client.force_authenticate(user=support)
        response = api_client.post(
            f'/api/pets/{pending_pet.pk}/activate/',
            {'coverage_start': str(past)},
            format='json',
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == PetModelChoices.STATUS_CHOICES.ACTIVE
        assert response.data['coverage_start'] == str(past)

    def test_support_approves_pet_with_future_date_becomes_approved(self, api_client, support, pending_pet, today):
        future = today + timedelta(days=30)
        api_client.force_authenticate(user=support)
        response = api_client.post(
            f'/api/pets/{pending_pet.pk}/activate/',
            {'coverage_start': str(future)},
            format='json',
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == PetModelChoices.STATUS_CHOICES.APPROVED
        assert response.data['coverage_start'] == str(future)

    def test_support_approves_pet_without_date_uses_today(self, api_client, support, pending_pet, today):
        api_client.force_authenticate(user=support)
        response = api_client.post(
            f'/api/pets/{pending_pet.pk}/activate/',
            {},
            format='json',
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == PetModelChoices.STATUS_CHOICES.ACTIVE
        assert response.data['coverage_start'] == str(today)

    def test_cannot_approve_already_active_pet(self, api_client, support, customer, today):
        active_pet = baker.make(
            'pets.Pet',
            owner=customer,
            species=PetModelChoices.SPECIES_CHOICES.DOG,
            birth_date=date(2020, 1, 1),
            status=PetModelChoices.STATUS_CHOICES.ACTIVE,
            coverage_start=today - timedelta(days=30),
        )
        api_client.force_authenticate(user=support)
        response = api_client.post(
            f'/api/pets/{active_pet.pk}/activate/',
            {'coverage_start': str(today)},
            format='json',
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_cannot_approve_already_approved_pet(self, api_client, support, customer, today):
        approved_pet = baker.make(
            'pets.Pet',
            owner=customer,
            species=PetModelChoices.SPECIES_CHOICES.CAT,
            birth_date=date(2021, 1, 1),
            status=PetModelChoices.STATUS_CHOICES.APPROVED,
            coverage_start=today + timedelta(days=10),
        )
        api_client.force_authenticate(user=support)
        response = api_client.post(
            f'/api/pets/{approved_pet.pk}/activate/',
            {'coverage_start': str(today)},
            format='json',
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_customer_cannot_approve_pet(self, api_client, customer, pending_pet, today):
        api_client.force_authenticate(user=customer)
        response = api_client.post(
            f'/api/pets/{pending_pet.pk}/activate/',
            {'coverage_start': str(today)},
            format='json',
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
