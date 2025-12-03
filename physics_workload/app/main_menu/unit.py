from django.conf import settings
from iommi.main_menu import M
from iommi.path import register_path_decoding

from app.models.task import Task
from app.models.unit import Unit
from app.pages.task import TaskDelete, TaskDetail, TaskEdit
from app.pages.unit import UnitCreate, UnitDelete, UnitDetail, UnitEdit, UnitList
from app.pages.unit.history import UnitHistoryDetail, UnitHistoryList
from app.pages.unit.task import UnitTaskCreate, UnitTaskLeadCreate

# Decodes "<unit>" in paths into `params.unit`
register_path_decoding(unit=Unit)
register_path_decoding(unit_history=lambda string, **_: Unit.history.get(history_id=int(string)))

# Added to the main menu
unit_submenu: M = M(
    display_name=Unit._meta.verbose_name_plural,
    icon=Unit.icon,
    include=lambda user, **_: user.is_authenticated,
    view=UnitList().as_view(),
    items=dict(
        create=M(
            icon=settings.ICON_CREATE,
            include=lambda user, **_: user.has_perm("app.add_unit"),
            view=UnitCreate().as_view(),
        ),
        detail=M(
            display_name=lambda unit, **_: unit.code,
            include=lambda user, unit, **_: user.has_perm("app.view_unit", unit),
            params={"unit"},
            path="<unit>/",
            url=lambda unit, **_: f"/{Unit.url_root}/{unit.pk}/",
            view=UnitDetail().as_view(),
            items=dict(
                edit=M(
                    icon=settings.ICON_EDIT,
                    view=UnitEdit().as_view(),
                    include=lambda user, unit, **_: user.has_perm("app.change_unit", unit),
                ),
                delete=M(
                    icon=settings.ICON_DELETE,
                    view=UnitDelete().as_view(),
                    include=lambda user, unit, **_: user.has_perm("app.delete_unit", unit),
                ),
                history=M(
                    icon=settings.ICON_HISTORY,
                    view=UnitHistoryList().as_view(),
                    items=dict(
                        detail=M(
                            display_name=lambda unit_history, **_: unit_history.history_date.date(),
                            params={"unit_history"},
                            path="<unit_history>/",
                            view=UnitHistoryDetail().as_view(),
                        )
                    ),
                ),
                create=M(
                    display_name="Create Task",
                    icon=settings.ICON_CREATE,
                    view=UnitTaskCreate().as_view(),
                    include=lambda user, **_: user.has_perm("app.add_task"),
                ),
                create_lead=M(
                    display_name="Create Lead Task",
                    include=lambda user, unit, **_: user.has_perm("app.add_task"),
                    icon="user-plus",
                    view=UnitTaskLeadCreate().as_view(),
                ),
                task_detail=M(
                    display_name=lambda task, **_: task.title,
                    icon=Task.icon,
                    params={"unit", "task"},
                    path="<task>/",
                    include=lambda user, task, **_: user.has_perm("app.view_task", task),
                    url=lambda task, **_: f"/{Unit.url_root}/{task.unit.pk}/{task.pk}/",
                    view=TaskDetail().as_view(),
                    items=dict(
                        edit=M(
                            icon=settings.ICON_EDIT,
                            view=TaskEdit().as_view(),
                            include=lambda user, task, **_: user.has_perm("app.edit_task", task),
                        ),
                        delete=M(
                            icon=settings.ICON_DELETE,
                            view=TaskDelete().as_view(),
                            include=lambda user, task, **_: user.has_perm("app.delete_task", task),
                        ),
                    ),
                ),
            ),
        ),
    ),
)
