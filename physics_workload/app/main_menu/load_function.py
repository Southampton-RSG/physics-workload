from django.conf import settings
from iommi.main_menu import M
from iommi.path import register_path_decoding

from app.models.load_function import LoadFunction
from app.pages.load_function import LoadFunctionCreate, LoadFunctionDelete, LoadFunctionDetail, LoadFunctionEdit, LoadFunctionList

# Decode <load_function> in paths so a LoadFunction object is in the view parameters.
register_path_decoding(load_function=LoadFunction)

# This is imported into the main menu tree.
load_function_submenu: M = M(
    display_name=LoadFunction._meta.verbose_name_plural,
    icon=LoadFunction.icon,
    include=lambda user, **_: user.is_authenticated,
    view=LoadFunctionList().as_view(),
    items=dict(
        create=M(
            icon=settings.ICON_CREATE,
            view=LoadFunctionCreate().as_view(),
            include=lambda user, **_: user.has_perm("app.add_loadfunction"),
        ),
        detail=M(
            display_name=lambda load_function, **_: load_function.name,
            include=lambda user, load_function, **_: user.has_perm("app.view_loadfunction", load_function),
            params={"load_function"},
            path="<load_function>/",
            url=lambda load_function, **_: f"/{LoadFunction.url_root}/{load_function.pk}/",
            view=LoadFunctionDetail().as_view(),
            items=dict(
                edit=M(
                    icon=settings.ICON_EDIT,
                    view=LoadFunctionEdit().as_view(),
                    include=lambda user, load_function, **_: user.has_perm("app.change_loadfunction", load_function),
                ),
                delete=M(
                    icon=settings.ICON_DELETE,
                    view=LoadFunctionDelete().as_view(),
                    include=lambda user, load_function, **_: user.has_perm("app.delete_loadfunction", load_function),
                ),
                # history=M(
                #     icon='clock-rotate-left',
                #     view=LoadFunctionHistory
                # )
            ),
        ),
    ),
)
