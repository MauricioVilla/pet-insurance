import pytest
from datetime import date, timedelta

from rest_framework.test import APIClient
from model_bakery import baker

from apps.users.constants import UserModelChoices
from apps.pets.constants import PetModelChoices


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def today():
    return date.today()


@pytest.fixture
def customer(db):
    return baker.make(
        'users.User',
        email='customer@test.com',
        role=UserModelChoices.ROLE_CHOICES.CUSTOMER,
        is_active=True,
    )


@pytest.fixture
def support(db):
    return baker.make(
        'users.User',
        email='support@test.com',
        role=UserModelChoices.ROLE_CHOICES.SUPPORT,
        is_active=True,
    )


@pytest.fixture
def pending_pet(customer):
    return baker.make(
        'pets.Pet',
        owner=customer,
        name='Rex',
        species=PetModelChoices.SPECIES_CHOICES.DOG,
        birth_date=date(2020, 1, 1),
        status=PetModelChoices.STATUS_CHOICES.PENDING,
    )
