from django.utils.html import format_html
from iommi import Menu, MenuItem, Page, Fragment, LAST, Column, menu

from app.assets import mathjax_js


class HeaderMenu(Menu):
    """
    The top bar menu on every page, linking to the functionality
    """
    home = MenuItem(
        url='/',
        display_name=format_html(
            '<i class="fa-solid fa-scale-balanced"></i>'
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
        url='/function/', display_name='Functions'
    )
    standard_loads = MenuItem(
        url='/load/', display_name='Standards'
    )

    login = MenuItem(
        display_name="Login",
        include=lambda request, **_: not request.user.is_authenticated,
        a__attrs__class={'btn btn-outline-secondary': True, 'nav-item': False},
    )
    logout = MenuItem(
        display_name="Logout",
        include=lambda request, **_: request.user.is_authenticated,
        a__attrs__class={'btn btn-secondary': True, 'nav-item': False},
    )


    class Meta:
        attrs__class = {
            'fixed-top': True,
        }


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


class ColumnModify(Column):
    class Meta:
        # include=lambda request, **_: request.user.is_staff,
        cell__value=lambda row, **_: row.get_absolute_url(),
        cell__template='app/modify_row.html',
        header__attrs__class={'text-center': True},
        after=LAST,

    @staticmethod
    def create(**kwargs) -> Column:
        """
        :return:
        """
        return Column(
            # include=lambda request, **_: request.user.is_staff,
            cell__value=lambda row, **_: row.get_absolute_url(),
            cell__template='app/modify_row.html',
            cell__attrs__class={'text-center': True},
            header__attrs__class={'text-center': True},
            sortable=False,
            after=LAST,
        )


from iommi import register_search_fields
from app.models.staff import Staff
from app.models.task import Task

register_search_fields(
     model=Staff, search_fields=['name', 'gender', 'academic_group'], allow_non_unique=True,
)
register_search_fields(
    model=Task, search_fields=['name'], allow_non_unique=True
)
