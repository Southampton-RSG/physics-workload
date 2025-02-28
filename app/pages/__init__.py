from django.utils.html import format_html, mark_safe
from iommi import Menu, MenuItem, Page, html, Action, Fragment, LAST, Asset, Header, Column

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
        tag = 'footer'
        attrs__class = {
            'fixed-bottom': True,
            'mt-5': True,
            'justify-content-around': True,
        }
        after = LAST


class BasePage(Page):
    """
    The base page with header and footer
    """
    menu = HeaderMenu()

    footer = FooterMenu()


class HeaderInstanceEdit(Header):
    """
    A header for a model being edited
    """
    class Meta:
        children__suffix=html.span(template='app/edit_suffix.html')


class HeaderInstanceCreate(Header):
    """
    A header for a model being edited
    """
    class Meta:
        children__suffix=html.span(template='app/create_suffix.html')


class HeaderInstanceDelete(Header):
    """
    A header for a model being deleted
    """
    class Meta:
        children__suffix=html.span(template='app/delete_suffix.html')


class HeaderInstanceDetail(Header):
    """
    A header, with a 'edit this model' button after it
    """
    class Meta:
        children__button=html.span(template='app/edit_button.html')
        attrs__class={'position-relative': True}


class HeaderList(Header):
    """
    A header, with a 'create new' button after it
    """
    class Meta:
        children__button=html.span(template='app/create_button.html')
        attrs__class={'position-relative': True}


class Equations(Fragment):
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
