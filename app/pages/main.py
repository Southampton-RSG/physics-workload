from django.urls import reverse_lazy
from django.utils.translation import gettext as _
from iommi import Menu, MenuItem, Page, html

from app.pages import BasePage


class IndexPage(BasePage):
    title = html.h1(_("Teaching Time Tool"))
    text = html.p("Select a thing")