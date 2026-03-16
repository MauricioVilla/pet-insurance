from model_utils import Choices


class UserModelChoices:
    ROLE_CHOICES = Choices(
        ('CUSTOMER', 'Customer'),
        ('SUPPORT', 'Support'),
        ('ADMIN', 'Admin'),
    )
