from django.urls import path
from django.template import Template
from iommi import html, Page
from iommi.experimental.main_menu import MainMenu, M, EXTERNAL

from app.pages.academic_group import academic_group_submenu
from app.pages.staff import staff_submenu
from app.pages.unit import unit_submenu
from app.pages.task import task_submenu
from app.pages.load_function import load_function_submenu
from app.pages.standard_load import StandardLoadDetail, StandardLoadList, StandardLoadEdit
from app.models import AcademicGroup, LoadFunction, Staff, Task, Unit, StandardLoad


main_menu = MainMenu(
    items=dict(
        # --------------------------------------------------------------------------------------------------------------
        # Staff
        # --------------------------------------------------------------------------------------------------------------
        staff=staff_submenu,
        # --------------------------------------------------------------------------------------------------------------
        # Units and their subsidiary tasks
        # --------------------------------------------------------------------------------------------------------------
        unit=unit_submenu,
        # --------------------------------------------------------------------------------------------------------------
        # Tasks
        # --------------------------------------------------------------------------------------------------------------
        task=task_submenu,

        # --------------------------------------------------------------------------------------------------------------
        # Academic Groups
        # --------------------------------------------------------------------------------------------------------------
        group=academic_group_submenu,

        # --------------------------------------------------------------------------------------------------------------
        # Load Functions
        # --------------------------------------------------------------------------------------------------------------
        function=load_function_submenu,

        # --------------------------------------------------------------------------------------------------------------
        # Standard Loads
        # --------------------------------------------------------------------------------------------------------------
        load=M(
            icon=StandardLoad.icon,
            view=lambda **_: StandardLoadList,
            include=lambda request, **_: request.user.is_authenticated,
            items=dict(
                detail=M(
                    open=True,
                    view=StandardLoadDetail,
                    display_name=lambda standard_load, **_: standard_load,
                    path='<standard_load>/',
                    url=lambda standard_load, **_: standard_load.get_absolute_url(),
                    params={'standard_load'},
                ),
            ),
        ),
    ),
)
