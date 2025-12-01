from django.urls import reverse_lazy
from django.views.generic import RedirectView
from iommi.main_menu import M, MainMenu

from django.urls import reverse_lazy, reverse

from app.main_menu.academic_group import academic_group_submenu
from app.main_menu.info import info_submenu
from app.main_menu.load_function import load_function_submenu
from app.main_menu.staff import staff_submenu
from app.main_menu.standard_load import standard_load_submenu
from app.main_menu.task import task_submenu
from app.main_menu.unit import unit_submenu
from app.pages.basic import AboutPage, PrivacyPage
from app.views import home_redirect


main_menu = MainMenu(
    items=dict(
        index=M(
            path="",
            render=False,
            view=RedirectView.as_view(url="/about/"),
        ),
        home=M(
            include=lambda user, **_: user.is_authenticated,
            render=False,
            view=home_redirect,
        ),
        privacy=M(
            render=False,
            view=PrivacyPage().as_view(),
        ),
        about=M(
            render=False,
            view=AboutPage().as_view()
        ),
        staff=staff_submenu,
        module=unit_submenu,
        task=task_submenu,
        group=academic_group_submenu,
        function=load_function_submenu,
        load=standard_load_submenu,
        info=info_submenu,
    ),
)
