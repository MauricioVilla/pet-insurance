from model_utils import Choices


class ClaimModelChoices:
    STATUS_CHOICES = Choices(
        ('SUBMITTED', 'Submitted'),
        ('PROCESSING', 'Processing'),
        ('IN_REVIEW', 'In Review'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    )
