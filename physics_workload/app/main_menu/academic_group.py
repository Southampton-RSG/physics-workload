from django.conf import settings
from iommi.main_menu import M
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
    view=AcademicGroupList().as_view(),
    items=dict(
        create=M(
            icon=settings.ICON_CREATE,
            view=AcademicGroupCreate().as_view(),
            include=lambda user, **_: user.has_perm("app.add_academicgroup"),
        ),
        detail=M(
            display_name=lambda academic_group, **_: academic_group.short_name,
            include=lambda user, academic_group, **_: user.has_perm("app.view_academicgroup", academic_group),
            params={"academic_group"},
            path="<academic_group>/",
            url=lambda academic_group, **_: academic_group.get_absolute_url(),
            view=AcademicGroupDetail().as_view(),
            items=dict(
                edit=M(
                    icon=settings.ICON_EDIT,
                    view=AcademicGroupEdit().as_view(),
                    include=lambda user, academic_group, **_: user.has_perm("app.change_academicgroup", academic_group),
                ),
                delete=M(
                    icon=settings.ICON_DELETE,
                    view=AcademicGroupDelete().as_view(),
                    include=lambda user, academic_group, **_: user.has_perm("app.delete_academicgroup", academic_group)
                ),
                history=M(
                    icon=settings.ICON_HISTORY,
                    view=AcademicGroupHistoryList().as_view(),
                    include=lambda user, academic_group, **_: user.has_perm("app.view_academicgroup", academic_group),
                ),
                create=M(
                    display_name="Create Task",
                    icon=settings.ICON_CREATE,
                    view=AcademicGroupTaskCreate().as_view(),
                    include=lambda user, **_: user.is_staff,
                ),
                task_detail=M(
                    display_name=lambda task, **_: task.title,
                    icon=Task.icon,
                    include=lambda user, task, **_: user.has_perm("app.view_task", task),
                    open=True,
                    params={"academic_group", "task"},
                    path="<task>/",
                    url=lambda task, **_: task.get_absolute_url(),
                    view=TaskDetail().as_view(),
                    items=dict(
                        edit=M(
                            icon=settings.ICON_EDIT,
                            view=TaskEdit().as_view(),
                            include=lambda user, **_: user.is_staff,
                        ),
                        delete=M(
                            icon=settings.ICON_DELETE,
                            view=TaskDelete().as_view(),
                            include=lambda user, **_: user.is_staff,
                        ),
                    ),
                ),
            ),
        ),
    ),
)
