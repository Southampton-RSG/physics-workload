from django.urls import path
from django.template import Template
from iommi import html, Page
from iommi.experimental.main_menu import MainMenu, M, EXTERNAL

from app.models.standard_load import get_current_standard_load
from app.pages.academic_group import AcademicGroupList, AcademicGroupDetail, AcademicGroupCreate, AcademicGroupDelete, AcademicGroupEdit
from app.pages.staff import StaffList, StaffDetail, StaffCreate, StaffEdit, StaffDelete
from app.pages.unit import UnitList, UnitDetail, UnitCreate, UnitEdit, UnitDelete, get_menu_units_for_user
from app.pages.task import TaskList, TaskDetail, TaskCreate, TaskEdit, TaskDelete
from app.pages.load_function import LoadFunctionList, LoadFunctionDetail, LoadFunctionCreate, LoadFunctionEdit, LoadFunctionDelete
from app.pages.standard_load import StandardLoadDetail
from app.auth import has_staff_access
from app.models import AcademicGroup, LoadFunction, Staff, Task, Unit, StandardLoad


main_menu = MainMenu(
    items=dict(
        staff=M(
            open=True,
            icon=Staff.icon,
            view=StaffList,
            include=lambda request, **_: request.user.is_authenticated,
            items=dict(
                detail=M(
                    view=StaffDetail,
                    display_name=lambda staff, **_: staff.name,
                    path='<staff>/',
                    url=lambda staff, **_: staff.get_absolute_url(),
                    params={'staff'},
                )
            )
        ),
        unit=M(
            open=True,
            icon=Unit.icon,
            display_name="Unit",
            view=UnitList,
            include=lambda request, **_: request.user.is_authenticated,
            items=dict(
                detail=M(
                    view=UnitDetail,
                    display_name=lambda unit, **_: unit.code,
                    path='<unit>/',
                    url=lambda unit, **_: unit.get_absolute_url(),
                    params={'unit'},
                    items=dict(
                        task_detail=M(
                            open=True,
                            icon=Task.icon,
                            view=TaskDetail,
                            display_name=lambda task, **_: task.name,
                            path='<task>/',
                            url=lambda task, **_: task.get_absolute_url(),
                            params={'unit', 'task'},

                        )
                    )
                )
            )
        ),
        task=M(
            icon=Task.icon,
            view=TaskList,
            include=lambda request, **_: request.user.is_authenticated,
            items=dict(
                detail=M(
                    open=True,
                    view=TaskDetail,
                    display_name=lambda task, **_: task.name,
                    path='<task>/',
                    url=lambda task, **_: task.get_absolute_url(),
                    params={'task'},
                )
            )
        ),
        group=M(
            open=True,
            icon=AcademicGroup.icon,
            view=AcademicGroupList,
            include=lambda request, **_: request.user.is_authenticated,
            items=dict(
                detail=M(
                    open=True,
                    view=AcademicGroupDetail,
                    display_name=lambda academic_group, **_: academic_group.short_name,
                    path='<academic_group>/',
                    url=lambda academic_group, **_: academic_group.get_absolute_url(),
                    params={'academic_group'},
                )
            )
        ),
        function=M(
            path='/function/',
            icon=LoadFunction.icon,
            view=LoadFunctionList,
            include=lambda request, **_: request.user.is_authenticated,
            items=dict(
                detail=M(
                    view=LoadFunctionDetail,
                    display_name=lambda load_function, **_: load_function.name,
                    path='<load_function>/',
                    url=lambda load_function, **_: load_function.get_absolute_url(),
                    params={'load_function'},
                )
            )
        ),
        load=M(
            path='/load/',
            icon=StandardLoad.icon,
            view=lambda **_: StandardLoadDetail(year=get_current_standard_load().year).as_view(),
            url=lambda **_: get_current_standard_load().get_absolute_url(),
            include=lambda request, **_: request.user.is_authenticated,
            items=dict(
                detail=M(
                    open=True,
                    view=StandardLoadDetail,
                    display_name=lambda standard_load, **_: standard_load,
                    path='<standard_load>/',
                    url=lambda standard_load, **_: standard_load.get_absolute_url(),
                    params={'standard_load'},
                )
            ),
        ),
    ),

)
