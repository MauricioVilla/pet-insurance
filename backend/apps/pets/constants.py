from model_utils import Choices


class PetModelChoices:
    SPECIES_CHOICES = Choices(
        ('DOG', 'Dog'),
        ('CAT', 'Cat'),
        ('OTHER', 'Other'),
    )

    STATUS_CHOICES = Choices(
        ('PENDING', 'Pending'),
        ('ACTIVE', 'Active'),
    )
