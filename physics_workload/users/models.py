"""
Custom users wrapper, in case they need expansion later.
"""

from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    # add additional fields in here

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def __repr__(self):
        return f"{self.first_name} {self.last_name}"
