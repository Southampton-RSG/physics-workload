from django.conf import settings
from iommi.experimental.main_menu import M
from iommi.path import register_path_decoding

from app.auth import has_access_decoder
from app.models import AcademicGroup, Task
from app.pages.academic_group import (
    AcademicGroupCreate,
    AcademicGroupDelete,
    AcademicGroupDetail,
    AcademicGroupEdit,
    AcademicGroupList,
    AcademicGroupTaskCreate,
)
from app.pages.academic_group.history import AcademicGroupHistoryList
from app.pages.task import TaskDelete, TaskDetail, TaskEdit

# Decodes "<academic_group>" in paths to add parmas.academic_group
register_path_decoding(
    academic_group=has_access_decoder(AcademicGroup, "You must be a member of this Group to view it."),
)

# Imported into the main menu
academic_group_submenu: M = M(
    display_name=AcademicGroup._meta.verbose_name_plural,
    icon=AcademicGroup.icon,
    include=lambda user, **_: user.is_authenticated,
    view=AcademicGroupList,
    items=dict(
        create=M(
            icon=settings.ICON_CREATE,
            view=AcademicGroupCreate,
            include=lambda user, **_: user.is_staff,
        ),
        detail=M(
            display_name=lambda academic_group, **_: academic_group.short_name,
            open=True,
            params={"academic_group"},
            path="<academic_group>/",
            url=lambda academic_group, **_: f"/{AcademicGroup.url_root}/{academic_group.code}/",
            view=AcademicGroupDetail,
            items=dict(
                edit=M(
                    icon=settings.ICON_EDIT,
                    view=AcademicGroupEdit,
                    include=lambda user, **_: user.is_staff,
                ),
                delete=M(
                    icon=settings.ICON_DELETE,
                    view=AcademicGroupDelete,
                    include=lambda user, **_: user.is_staff,
                ),
                history=M(
                    icon=settings.ICON_HISTORY,
                    view=AcademicGroupHistoryList,
                    include=lambda user, **_: user.is_staff,
                ),
                create=M(
                    display_name="Create Task",
                    icon=settings.ICON_CREATE,
                    view=AcademicGroupTaskCreate,
                    include=lambda user, **_: user.is_staff,
                ),
                task_detail=M(
                    display_name=lambda task, **_: task.name,
                    icon=Task.icon,
                    open=True,
                    params={"academic_group", "task"},
                    path="<task>/",
                    url=lambda task, **_: f"/{AcademicGroup.url_root}/{task.academic_group.pk}/{task.pk}/",
                    view=TaskDetail,
                    items=dict(
                        edit=M(
                            icon=settings.ICON_EDIT,
                            view=TaskEdit,
                            include=lambda user, **_: user.is_staff,
                        ),
                        delete=M(
                            icon=settings.ICON_DELETE,
                            view=TaskDelete,
                            include=lambda user, **_: user.is_staff,
                        ),
                    ),
                ),
            ),
        ),
    ),
)
