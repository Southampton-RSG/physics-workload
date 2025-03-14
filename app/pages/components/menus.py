from django.utils.html import format_html
from iommi import Menu, MenuItem, LAST


class HeaderMenu(Menu):
    """
    The top bar menu on every page, linking to the functionality
    """
    home = MenuItem(
        url='/',
        display_name=format_html(

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
