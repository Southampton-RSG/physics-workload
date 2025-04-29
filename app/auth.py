"""
Adds access-checking functions that test the permissions on the model.
"""
from typing import Type, Callable, Any

from django.contrib.auth.models import AnonymousUser, AbstractUser
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest

from app.models.common import ModelCommon


def has_access_decoder(model: Type[ModelCommon], message: str) -> Callable[[str, HttpRequest, Any], ModelCommon]:
    """
    Factory for making access decoders for a given model
    :param model: The model to create the decoder for
    :return: A function that decodes access for that model
    """
    def has_access_decoder_inner(string: str, request: HttpRequest, **_) -> ModelCommon:
        """
        Given a URL string key and a user, returns the model associated with that string if the user has permission.
        :param string: URL component (e.g. `staff/<staff_pk>/`).
        :param user: Django user instance.
        :exception PermissionDenied: If the user doesn't have model permissions.
        :return: The model if the user has permission.
        """
        instance: ModelCommon = model.objects.get(pk=string.strip())
        if instance.has_access(request.user):
            return instance

        raise PermissionDenied(message)

    return has_access_decoder_inner


def has_staff_access(user: AbstractUser|AnonymousUser) -> bool:
    """
    Checks if the user is signed in and staff, or if security is off for debugging.

    :param user:
    :return:
    """
    if user.is_authenticated and user.is_staff:
        return True
    else:
        return False
