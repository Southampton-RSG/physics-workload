from abc import abstractmethod

from django.contrib.auth.models import AbstractUser, AnonymousUser
from django.template.loader import render_to_string
from django.urls import reverse
from django.db.models import Model
from django.http import HttpRequest


class ModelCommonMixin(Model):
    """
    Contains the framework for a DB model to have an icon and title associated with it

    Classes implement `icon` (a font-awesome icon name) and `url_root` (the Django URL resolver root for that model).
    """
    class Meta:
        abstract = True

    @property
    @abstractmethod
    def icon(self) -> str:
        """
        :return: The icon shown on the list views e.t.c.
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def url_root(self) -> str:
        """
        :return: The root of the URLs for this model, to which `_detail`, `_edit` e.t.c. will be added
        """
        raise NotImplementedError()

    def get_absolute_url(self) -> str:
        """
        :return: The URL for the detail view of this particular instance of the model
        """
        return reverse(type(self).url_root+'_detail', args=[self.pk])

    def get_instance_header(self, text: str|None = None) -> str:
        """
        Creates a header for a view for an instance of this model.
        :param text: The text to use for the header, if not just the string representation of the instance.
        :return: The rendered template, for use on the page.
        """
        return render_to_string(
            template_name='app/header/header.html',
            context={
                'icon': self.icon, 'text': text if text else self
            }
        )

    @classmethod
    def get_model_url(cls) -> str:
        """
        Equivalent to `get_absolute_url()` for model list.
        :return: The URL for the view listing all of this model
        """
        return reverse(cls.url_root+'_list')

    @classmethod
    def get_model_header(cls) -> str:
        """
        Creates a header for the view listing all of this model.
        :return: The rendered template, for use on the page.
        """
        return render_to_string(
            template_name='app/header/header.html',
            context={
                'icon': cls.icon, 'url': cls.get_model_url(),
                'text': cls._meta.verbose_name_plural.title()
            }
        )

    @abstractmethod
    def has_access(self, user: AbstractUser|AnonymousUser) -> bool:
        """
        :param user: The user checking access.
        :return: Whether or not the user has permission to view this model.
        """
        raise NotImplementedError()
