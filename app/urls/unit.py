from django.conf import settings
from iommi.experimental.main_menu import M
from iommi.path import register_path_decoding

from app.auth import has_access_decoder
from app.models.task import Task
from app.models.unit import Unit
from app.pages.task import TaskDelete, TaskDetail, TaskEdit
from app.pages.unit import UnitCreate, UnitDelete, UnitDetail, UnitEdit, UnitList
from app.pages.unit.history import UnitHistoryDetail, UnitHistoryList
from app.pages.unit.task import UnitTaskCreate, UnitTaskLeadCreate

# Decodes "<unit>" in paths into `params.unit`
register_path_decoding(
    unit=has_access_decoder(Unit, "You must be assigned to a Unit to view it"),
)
register_path_decoding(
    unit_history=lambda string, **_: Unit.history.get(history_id=int(string)),
)

# Added to the main menu
unit_submenu: M = M(
    icon=Unit.icon,
    include=lambda request, **_: request.user.is_authenticated,
    view=UnitList,
    items=dict(
        create=M(
            icon=settings.ICON_CREATE,
            include=lambda request, **_: request.user.is_staff,
            view=UnitCreate,
        ),
        detail=M(
            display_name=lambda unit, **_: unit.code,
            open=True,
            params={"unit"},
            path="<unit>/",
            url=lambda unit, **_: f"/{Unit.url_root}/{unit.pk}/",
            view=UnitDetail,
            items=dict(
                edit=M(
                    icon=settings.ICON_EDIT,
                    view=UnitEdit,
                    include=lambda request, **_: request.user.is_staff,
                ),
                delete=M(
                    icon=settings.ICON_DELETE,
                    view=UnitDelete,
                    include=lambda request, **_: request.user.is_staff,
                ),
                history=M(
                    icon=settings.ICON_HISTORY,
                    view=UnitHistoryList,
                    items=dict(
                        detail=M(
                            display_name=lambda unit_history, **_: unit_history.history_date.date(),
                            params={"unit_history"},
                            path="<unit_history>/",
                            view=UnitHistoryDetail,
                        )
                    ),
                ),
                create=M(
                    display_name="Create Task",
                    icon=settings.ICON_CREATE,
                    view=UnitTaskCreate,
                    include=lambda request, **_: request.user.is_staff,
                ),
                create_lead=M(
                    display_name="Create Lead Task",
                    include=lambda request, **_: request.user.is_staff,
                    icon="user-plus",
                    view=UnitTaskLeadCreate,
                ),
                task_detail=M(
                    display_name=lambda task, **_: task.name,
                    icon=Task.icon,
                    open=True,
                    params={"unit", "task"},
                    path="<task>/",
                    url=lambda task, **_: f"/{Unit.url_root}/{task.unit.pk}/{task.pk}/",
                    view=TaskDetail,
                    items=dict(
                        edit=M(
                            icon=settings.ICON_EDIT,
                            view=TaskEdit,
                            include=lambda request, **_: request.user.is_staff,
                        ),
                        delete=M(
                            icon=settings.ICON_DELETE,
                            view=TaskDelete,
                            include=lambda request, **_: request.user.is_staff,
                        ),
                    ),
                ),
            ),
        ),
    ),
)
