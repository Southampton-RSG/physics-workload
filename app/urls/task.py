from django.conf import settings
from iommi.path import register_path_decoding
from iommi.experimental.main_menu import M

from app.auth import has_access_decoder
from app.models.task import Task
from app.pages.task import TaskList, TaskCreate, TaskDetail, TaskEdit, TaskDelete, TaskFullTimeCreate


# Decode <task> in paths so a LoadFunction object is in the view parameters.
register_path_decoding(
    task=has_access_decoder(Task, "You must be assigned to a Task to view it."),
)

# This is imported into the main menu tree.
task_submenu: M = M(
    display_name=Task._meta.verbose_name_plural,
    icon=Task.icon,
    include=lambda request, **_: request.user.is_authenticated,
    view=TaskList,

    items=dict(
        create=M(
            icon=settings.ICON_CREATE,
            include=lambda request, **_: request.user.is_staff,
            path='create/',
            view=TaskCreate,
        ),
        create_full_time=M(
            display_name="Create Full-Time Task",
            icon='square-plus',
            path='create/full-time/',
            include=lambda request, **_: request.user.is_staff,
            view=TaskFullTimeCreate,
        ),
        detail=M(
            display_name=lambda task, **_: task.name,
            open=True,
            params={'task'},
            path='<task>/',
            url=lambda task, **_: f"/{Task.url_root}/{task.pk}/",
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
                # history=M(
                #     icon='clock-rotate-left',
                #     view=TaskHistory,
                # )
            )
        )
    )
)
