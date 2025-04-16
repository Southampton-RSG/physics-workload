from django.urls import path
from django.template import Template
from iommi import html, Page
from iommi.experimental.main_menu import MainMenu, M, EXTERNAL

from app.pages.academic_group import AcademicGroupList, AcademicGroupDetail, AcademicGroupCreate, AcademicGroupDelete, AcademicGroupEdit
from app.pages.staff import StaffList, StaffDetail, StaffCreate, StaffEdit, StaffDelete, StaffHistoryList, StaffHistoryDetail
from app.pages.unit import UnitList, UnitDetail, UnitCreate, UnitEdit, UnitDelete, get_menu_units_for_user, \
    UnitTaskCreate
from app.pages.task import TaskList, TaskDetail, TaskCreate, TaskEdit, TaskDelete
from app.pages.load_function import load_function_submenu
from app.pages.standard_load import StandardLoadDetail, StandardLoadList, StandardLoadEdit
from app.auth import has_staff_access
from app.models import AcademicGroup, LoadFunction, Staff, Task, Unit, StandardLoad


main_menu = MainMenu(
    items=dict(
        # --------------------------------------------------------------------------------------------------------------
        # Staff
        # --------------------------------------------------------------------------------------------------------------
        staff=M(
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
                    items=dict(
                        edit=M(
                            icon='pencil',
                            view=StaffEdit,
                            include=lambda request, **_: request.user.is_staff,
                        ),
                        delete=M(
                            icon='trash',
                            view=StaffDelete,
                            include=lambda request, **_: request.user.is_staff,
                        ),
                        history=M(
                            icon='clock-rotate-left',
                            view=StaffHistoryList,
                            items=dict(
                                detail=M(
                                    view=StaffHistoryDetail,
                                    display_name=lambda staff_history, **_: staff_history.history_date.date(),
                                    path='<staff_history>/',
                                    params={'staff_history'},
                                )
                            )
                        ),
                    ),
                ),
                create=M(
                    icon="plus",
                    view=StaffCreate,
                    include=lambda request, **_: request.user.is_staff,
                ),
            ),
        ),

        # --------------------------------------------------------------------------------------------------------------
        # Units and their subsidiary tasks
        # --------------------------------------------------------------------------------------------------------------
        unit=M(
            icon=Unit.icon,
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
                        edit=M(
                            icon='pencil',
                            view=UnitEdit,
                            include=lambda request, **_: request.user.is_staff,
                        ),
                        delete=M(
                            icon='trash',
                            view=UnitDelete,
                            include=lambda request, **_: request.user.is_staff,
                        ),
                        # history=M(
                        #     icon='clock-rotate-left',
                        #     view=UnitHistory,
                        # ),
                        task_detail=M(
                            icon=Task.icon,
                            view=TaskDetail,
                            display_name=lambda task, **_: task.name,
                            path='<task>/',
                            url=lambda task, **_: task.get_absolute_url(),
                            params={'unit', 'task'},
                            items=dict(
                                edit=M(
                                    icon='pencil',
                                    view=TaskEdit,
                                    include=lambda request, **_: request.user.is_staff,
                                ),
                                delete=M(
                                    icon='trash',
                                    view=TaskDelete,
                                    include=lambda request, **_: request.user.is_staff,
                                )
                            )
                        ),
                        create = M(
                            display_name="Create Task",
                            icon='plus',
                            view=UnitTaskCreate,
                            include=lambda request, **_: request.user.is_staff,
                        ),
                    ),
                ),
                create=M(
                    icon="plus",
                    view=UnitCreate,
                    include=lambda request, **_: request.user.is_staff,
                ),
            ),
        ),

        # --------------------------------------------------------------------------------------------------------------
        # Tasks
        # --------------------------------------------------------------------------------------------------------------
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
                    items=dict(
                        edit=M(
                            icon='pencil',
                            view=TaskEdit,
                            include=lambda request, **_: request.user.is_staff,
                        ),
                        delete=M(
                            icon='trash',
                            view=TaskDelete,
                            include=lambda request, **_: request.user.is_staff,
                        ),
                        # history=M(
                        #     icon='clock-rotate-left',
                        #     view=TaskHistory,
                        # )
                    ),
                ),
                create = M(
                    icon="plus",
                    view=TaskCreate,
                    include=lambda request, **_: request.user.is_staff,
                ),
            ),
        ),

        # --------------------------------------------------------------------------------------------------------------
        # Academic Groups
        # --------------------------------------------------------------------------------------------------------------
        group=M(
            icon=AcademicGroup.icon,
            view=AcademicGroupList,
            include=lambda request, **_: request.user.is_authenticated,
            items=dict(
                detail=M(
                    view=AcademicGroupDetail,
                    display_name=lambda academic_group, **_: academic_group.short_name,
                    path='<academic_group>/',
                    url=lambda academic_group, **_: academic_group.get_absolute_url(),
                    params={'academic_group'},
                    items=dict(
                        edit=M(
                            icon='pencil',
                            view=AcademicGroupEdit,
                            include=lambda request, **_: request.user.is_staff,
                        ),
                        delete=M(
                            icon='trash',
                            view=AcademicGroupDelete,
                            include=lambda request, **_: request.user.is_staff,
                        ),
                        # history=M(
                        #     icon='clock-rotate-left',
                        #     view=AcademicGroupHistory,
                        # )
                    ),
                ),
                create=M(
                    icon="plus",
                    view=AcademicGroupCreate,
                    include=lambda request, **_: request.user.is_staff,
                ),
            ),
        ),

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
