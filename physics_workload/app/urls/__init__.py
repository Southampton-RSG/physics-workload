from django.urls import path
from iommi.experimental.main_menu import MainMenu

from app.pages.basic import AboutPage, PrivacyPage
from app.urls.academic_group import academic_group_submenu
from app.urls.info import info_submenu
from app.urls.load_function import load_function_submenu
from app.urls.staff import staff_submenu
from app.urls.standard_load import standard_load_submenu
from app.urls.task import task_submenu
from app.urls.unit import unit_submenu
from app.views import home_view_redirect

main_menu = MainMenu(
    items=dict(
        staff=staff_submenu,
        module=unit_submenu,
        task=task_submenu,
        group=academic_group_submenu,
        function=load_function_submenu,
        load=standard_load_submenu,
        info=info_submenu,
    ),
)

urlpatterns = [
    # The home page
    path("", home_view_redirect, name="home"),
    path("about/", AboutPage().as_view(), name="about"),
    path("privacy/", PrivacyPage().as_view(), name="privacy"),
] + main_menu.urlpatterns()
