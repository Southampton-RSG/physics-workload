from abc import abstractmethod

from django.conf import settings
from django.contrib.auth.models import AbstractUser, AnonymousUser
from django.template.loader import render_to_string
from django.urls import reverse
from django.db.models import Model
from django.http import HttpRequest

from model_utils.models import SoftDeletableModel

from iommi import Fragment, Header, html
from simple_history.models import HistoricalRecords


class ModelCommon(SoftDeletableModel):
    """
    Contains the framework for a DB model to have an icon and title associated with it

    Classes implement `icon` (a font-awesome icon name) and `url_root` (the Django URL resolver root for that model).
    """
    history = HistoricalRecords(inherit=True)

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

    def get_absolute_url_authenticated(self, user: AbstractUser|AnonymousUser|None) -> str:
        """
        :param user: The user to check authorisation for.
        :return: The absolute URL for the detail view of this particular instance of the model if allowed, or blank.
        """
        if settings.DEBUG_ACCESS:
            return self.get_absolute_url()
        elif user and user.is_authenticated and (user.is_staff or self.has_access(user)):
            return self.get_absolute_url()
        else:
            return ''

    def get_instance_header(self, text: str|None = None) -> str:
        """
        Creates a header for a view for an instance of this model.
        :param text: The text to use for the header, if not just the string representation of the instance.
        :return: The rendered template, for use on the page.
        """
        # return html.span(
        #     children__icon=html.i(attrs__class={'fa-solid': True, f'fa-{self.icon}': True}),
        #     children__header=Header(text if text else f"{self}")
        # )

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
    def get_model_header(cls, suffix: str|None = None) -> str:
        """
        Creates a header for the view listing all of this model.
        :return: The rendered template, for use on the page.
        """
        return render_to_string(
            template_name='app/header/header.html',
            context={
                'icon': cls.icon, 'url': cls.get_model_url(),
                'text': cls._meta.verbose_name_plural.title()+(f' / {suffix}' if suffix else '')
            }
        )

    @classmethod
    def get_model_header_singular(cls, suffix: str|None = None) -> str:
        """
        Creates a header for a create view for this model.
        :return: The rendered template, for use on the page.
        """
        return render_to_string(
            template_name='app/header/header.html',
            context={
                'icon': cls.icon, 'url': cls.get_model_url(),
                'text': cls._meta.verbose_name.title()+(f' / {suffix}' if suffix else '')
            }
        )

    @abstractmethod
    def has_access(self, user: AbstractUser|AnonymousUser) -> bool:
        """
        :param user: The user checking access.
        :return: True if debug auth is on or the user is staff.
        """
        if settings.DEBUG_ACCESS or user.is_staff:
            return True
        else:
            return False
