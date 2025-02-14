from django.utils.html import format_html, mark_safe
from iommi import Menu, MenuItem, Page, html


class TopMenu(Menu):
    """
    Top menu shown on every page
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
    module_list = MenuItem(
        url='/module/', display_name="Modules"
    )
    task_school_list = MenuItem(
        url='/task/school/', display_name="School Tasks"
    )
    load_functions = MenuItem(
        url='/function/', display_name='Load Functions'
    )
    standard_loads = MenuItem(
        url='/load/', display_name='Standard Loads'
    )

    class Meta:
        attrs__class = {'fixed-top': True}


class BasePage(Page):
    menu = TopMenu()
