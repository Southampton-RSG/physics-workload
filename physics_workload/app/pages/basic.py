from iommi import Fragment, Header, Page

from app.forms.info import InfoForm
from app.models import Info


class PrivacyPage(Page):
    """
    Contains the privacy statement
    """

    text = Fragment(template="app/basic/privacy.html")


class AboutPage(Page):
    title = Header("Teaching Time Tool")
    info = InfoForm(
        instance=lambda **_: Info.objects.get(page="about"),
    )
