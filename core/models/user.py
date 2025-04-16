from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    class Role(models.TextChoices):
        MOBILE_TECHNICIAN = 'MT', 'Mobile Technician'
        NEUROLOGIST = 'NR', 'Neurologist'
    
    role = models.CharField(
        max_length=2,
        choices=Role.choices,
        default=Role.MOBILE_TECHNICIAN
    )
