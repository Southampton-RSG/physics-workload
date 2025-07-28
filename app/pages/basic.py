from django.conf import settings
from django.template import Template
from iommi import Action, Fragment, Header, Page, html

from app.models import Info


class PrivacyPage(Page):
    """
    Contains the privacy statement
    """
    text = Fragment(
        template='app/basic/privacy.html'
    )


class AboutPage(Page):
    title = Header(
        "Teaching Time Tool"
    )
    info = html.div(
        Template("{{ page.extra_evaluated.info.get_html | safe }}"),
        attrs__class={"position-relative": True},
        children__edit=Action.icon(
            display_name=" ",  # If it's empty/none, it's 'Edit'
            icon=settings.ICON_EDIT,
            attrs__class={
                'btn': True, 'btn-warning': True, 'btn-sm': True,
                'position-absolute': True, 'bottom-0': True, 'end-0': True,
            },
            include=lambda user, **_: user.is_staff,
            attrs__href=lambda **_: Info.objects.get(page='about').get_edit_url(),
        )
    )

    class Meta:
        extra_evaluated__info = lambda **_: Info.objects.get(page='about')
