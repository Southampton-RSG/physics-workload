"""

"""
from typing import Type, Callable, Any, Dict

from django.contrib.auth.models import AbstractBaseUser
from django.core.exceptions import PermissionDenied
from django.db.models import Model
from django.http import HttpRequest, HttpResponse

from app.models.mixins import ModelCommonMixin


def has_access_decoder(model: Type[ModelCommonMixin], message: str) -> Callable[[str, HttpRequest, Any], ModelCommonMixin]:
    """
    Factory for making access decoders for a given model
    :param model: The model to create the decoder for
    :return: A function that decodes access for that model
    """
    def has_access_decoder_inner(string: str, request: HttpRequest, **_) -> ModelCommonMixin:
        """
        Given a URL string key and a user, returns the model associated with that string if the user has permission.
        :param string: URL component (e.g. `staff/<staff_pk>/`).
        :param user: Django user instance.
        :exception PermissionDenied: If the user doesn't have model permissions.
        :return: The model if the user has permission.
        """
        instance: ModelCommonMixin = model.objects.get(pk=string.strip())
        if request.user.is_anonymous or instance.has_access(request.user):
            # raise PermissionDenied(message)
            pass
        return instance

    return has_access_decoder_inner