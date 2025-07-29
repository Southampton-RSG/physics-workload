from django.conf import settings
from django.template import Template
from iommi import Action, Form

from app.models import Info


class InfoForm(Form):
    """
    Form used for showing the 'Info' element at the top of various pages.

    Redirects to the 'page' the info is for on submission.
    """

    class Meta:
        auto = dict(
            model=Info,
            include=["text"],
        )
        fields__text__template = Template("{% load markdownify %}{{ field.value | markdownify }}")
        attrs__class = {"position-relative": True}
        actions__edit = Action.icon(
            display_name=" ",  # If it's empty/none, it's 'Edit'
            icon=settings.ICON_EDIT,
            attrs__class={
                "btn": True,
                "btn-warning": True,
                "btn-sm": True,
                "position-absolute": True,
                "bottom-0": True,
                "end-0": True,
            },
            include=lambda user, **_: user.is_staff,
            attrs__href=lambda instance, **_: instance.get_edit_url(),
        )
        extra__redirect_to = lambda instance, **_: instance.get_absolute_url()
