from abc import ABC, abstractmethod
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.db.models import Model


class ModelIconMixin(Model):
    """
    Contains the framework for a DB model to have an icon and title associated with it

    Classes implement `icon` (a font-awesome icon name) and `url_root` (the Django URL resolver root for that model).
    """
    class Meta:
        abstract = True

    def get_absolute_url(self) -> str:
        """
        :return: The URL for the detail view of this particular instance of the model
        """
        return reverse_lazy(type(self).url_root+'_detail', args=[self.pk])


    def get_instance_header(self, text: str|None = None) -> str:
        """
        :param text: The text to use for the header, if not just the string representation of the instance.
        :return:
        """
        return render_to_string(
            template_name='app/header/header.html',
            context={
                'icon': self.icon, 'url': self.get_absolute_url(),
                'text': text if text else self
            }
        )

    @classmethod
    def get_model_url(cls) -> str:
        """
        :return: The URL for the view listing all of this model
        """
        return reverse_lazy(cls.url_root+'_list')

    @classmethod
    def get_model_header(cls) -> str:
        return render_to_string(
            template_name='app/header/header.html',
            context={
                'icon': cls.icon, 'url': cls.get_model_url(),
                'text': cls._meta.verbose_name_plural.title()
            }
        )
