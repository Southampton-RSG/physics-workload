from iommi.path import register_path_decoding
from iommi.experimental.main_menu import M

from app.auth import has_access_decoder
from app.models import AcademicGroup, Task
from app.pages.task import TaskEdit, TaskDelete, TaskDetail
from app.pages.academic_group import AcademicGroupTaskCreate, AcademicGroupCreate, AcademicGroupEdit, AcademicGroupDelete, AcademicGroupList, AcademicGroupDetail


# Decodes "<academic_group>" in paths to add parmas.academic_group
register_path_decoding(
    academic_group=has_access_decoder(AcademicGroup, "You must be a member of this Group to view it."),
)

# Imported into the main menu
academic_group_submenu: M = M(
    display_name=AcademicGroup._meta.verbose_name_plural,
    icon=AcademicGroup.icon,
    include=lambda request, **_: request.user.is_authenticated,
    view=AcademicGroupList,

    items=dict(
        create=M(
            icon="plus",
            view=AcademicGroupCreate,
            include=lambda request, **_: request.user.is_staff,
        ),
        detail=M(
            display_name=lambda academic_group, **_: academic_group.short_name,
            open=True,
            params={'academic_group'},
            path='<academic_group>/',
            url=lambda academic_group, **_: f"/{AcademicGroup.url_root}/{academic_group.code}/",
            view=AcademicGroupDetail,

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

                create=M(
                    display_name="Create Task",
                    icon='plus',
                    view=AcademicGroupTaskCreate,
                    include=lambda request, **_: request.user.is_staff,
                ),
                task_detail=M(
                    display_name=lambda task, **_: task.name,
                    icon=Task.icon,
                    open=True,
                    params={'academic_group', 'task'},
                    path='<task>/',
                    url=lambda task, **_: f"/{AcademicGroup.url_root}/{task.academic_group.pk}/{task.pk}/",
                    view=TaskDetail,

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
                    )
                ),

            ),
        )
    )
)
