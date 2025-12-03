from django.conf import settings
from iommi.main_menu import M
from iommi.path import register_path_decoding

from app.models.task import Task
from app.pages.task import TaskCreate, TaskDelete, TaskDetail, TaskEdit, TaskFullTimeCreate, TaskList

# Decode <task> in paths so a LoadFunction object is in the view parameters.
register_path_decoding(task=Task)

# This is imported into the main menu tree.
task_submenu: M = M(
    display_name=Task._meta.verbose_name_plural,
    icon=Task.icon,
    include=lambda user, **_: user.is_authenticated,
    view=TaskList().as_view(),
    items=dict(
        create=M(
            icon=settings.ICON_CREATE,
            include=lambda user, **_: user.has_perm("app.add_task"),
            view=TaskCreate().as_view(),
        ),
        create_full_time=M(
            display_name="Create Full-Time Task",
            icon="square-plus",
            include=lambda user, **_: user.has_perm("app.add_task"),
            view=TaskFullTimeCreate().as_view(),
        ),
        detail=M(
            display_name=lambda task, **_: task.name,
            include=lambda user, task, **_: user.has_perm("app.view_task", task),
            params={"task"},
            path="<task>/",
            url=lambda task, **_: f"/{Task.url_root}/{task.pk}/",
            view=TaskDetail().as_view(),
            items=dict(
                edit=M(
                    icon=settings.ICON_EDIT,
                    include=lambda user, task, **_: user.has_perm("app.change_task", task),
                    view=TaskEdit().as_view(),
                ),
                delete=M(
                    icon=settings.ICON_DELETE,
                    include=lambda user, task, **_: user.has_perm("app.delete_task", task),
                    view=TaskDelete().as_view(),
                ),
                # history=M(
                #     icon='clock-rotate-left',
                #     view=TaskHistory,
                # )
            ),
        ),
    ),
)
