from django.conf import settings
from iommi.main_menu import M
from iommi.path import register_path_decoding


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


# Decodes "<academic_group>" in paths to add academic_group to params
register_path_decoding(academic_group=AcademicGroup)

# Imported into the main menu
academic_group_submenu: M = M(
    display_name=AcademicGroup._meta.verbose_name_plural,
    icon=AcademicGroup.icon,
    include=lambda user, **_: user.is_authenticated,
    view=AcademicGroupList().as_view(),
    items=dict(
        create=M(
            icon=settings.ICON_CREATE,
            include=lambda user, **_: user.has_perm("app.add_academicgroup"),
            view=AcademicGroupCreate().as_view(),
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
                    include=lambda user, academic_group, **_: user.has_perm("app.change_academicgroup", academic_group),
                    view=AcademicGroupEdit().as_view(),
                ),
                delete=M(
                    icon=settings.ICON_DELETE,
                    include=lambda user, academic_group, **_: user.has_perm("app.delete_academicgroup", academic_group),
                    view=AcademicGroupDelete().as_view(),
                ),
                history=M(
                    icon=settings.ICON_HISTORY,
                    include=lambda user, academic_group, **_: user.has_perm("app.view_academicgroup", academic_group),
                    view=AcademicGroupHistoryList().as_view(),
                ),
                create=M(
                    display_name="Create Task",
                    icon=settings.ICON_CREATE,
                    include=lambda user, **_: user.has_perm("app.add_task"),
                    view=AcademicGroupTaskCreate().as_view(),
                ),
                task_detail=M(
                    display_name=lambda task, **_: task.title,
                    icon=Task.icon,
                    include=lambda user, task, **_: user.has_perm("app.view_task", task),
                    params={"academic_group", "task"},
                    path="<task>/",
                    url=lambda task, **_: task.get_absolute_url(),
                    view=TaskDetail().as_view(),
                    items=dict(
                        edit=M(
                            icon=settings.ICON_EDIT,
                            include=lambda user, task, **_: user.has_perm("edit_task", task),
                            view=TaskEdit().as_view(),
                        ),
                        delete=M(
                            icon=settings.ICON_DELETE,
                            include=lambda user, task, **_: user.has_perm("delete_task", task),
                            view=TaskDelete().as_view(),
                        ),
                    ),
                ),
            ),
        ),
    ),
)
