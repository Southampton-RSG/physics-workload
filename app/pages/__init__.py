from django.utils.html import format_html, mark_safe
from iommi import Menu, MenuItem, Page, html, Action, Fragment, LAST, Asset

from app.assets import mathjax_js



class HeaderMenu(Menu):
    """
    The top bar menu on every page, linking to the functionality
    """
    home = MenuItem(
        url='/',
        display_name=format_html(
            '<i class="fa-solid fa-sun"></i>'
        ),
    )
    groups_list = MenuItem(
        url='/group/', display_name="Groups"
    )
    staff_list = MenuItem(
        url='/staff/', display_name="Staff"
    )
    unit_list = MenuItem(
        url='/unit/', display_name="Units"
    )
    task_school_list = MenuItem(
        url='/task/', display_name="Tasks"
    )
    load_functions = MenuItem(
        url='/function/', display_name='Load Functions'
    )
    standard_loads = MenuItem(
        url='/load/', display_name='Standard Loads'
    )

    class Meta:
        attrs__class = {'fixed-top': True}


class FooterMenu(Menu):
    """
    The bottom bar menu on every page, linking to GDPR e.t.c.
    """
    rsg = MenuItem(
        url='https://rsg.soton.ac.uk', display_name='RSG'
    )

    gdpr = MenuItem(
        url='/privacy/', display_name='GDPR'
    )

    class Meta:
        attrs__class = {
            'fixed-bottom': True,
            'justify-content-around': True,
        }


class BasePage(Page):
    """
    The base page with header and footer
    """
    menu = HeaderMenu()
    footer = FooterMenu()


class TitleEdit(Fragment):
    """
    A title, with a 'edit this model' button after it
    """
    class Meta:
        tag = 'h1'
        children__edit=html.span(template='app/edit_button.html')
        attrs__class={'position-relative': True}


class TitleCreate(Fragment):
    """
    A title, with a 'create new' button after it
    """
    class Meta:
        tag = 'h1'
        children__edit=html.span(template='app/create_button.html')
        attrs__class={'position-relative': True}


class MathJax(Fragment):
    """
    A block of text containing LaTeX equations
    """
    class Meta:
        tag = 'p'
        assets = mathjax_js


class ColOpts(dict):
    def __init__(
        self, display_name=None, group=None, cell_value=None, **kwargs
    ):
        super().__init__(**kwargs)