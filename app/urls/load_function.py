from django.conf import settings
from iommi.experimental.main_menu import M
from iommi.path import register_path_decoding

from app.models.load_function import LoadFunction
from app.pages.load_function import LoadFunctionCreate, LoadFunctionDelete, LoadFunctionDetail, LoadFunctionEdit, LoadFunctionList

# Decode <load_function> in paths so a LoadFunction object is in the view parameters.
register_path_decoding(
    load_function=lambda string, **_: LoadFunction.objects.get(pk=int(string))
)

# This is imported into the main menu tree.
load_function_submenu: M = M(
    display_name=LoadFunction._meta.verbose_name_plural,
    icon=LoadFunction.icon,
    include=lambda request, **_: request.user.is_authenticated,
    view=LoadFunctionList,

    items=dict(
        create=M(
            icon=settings.ICON_CREATE,
            view=LoadFunctionCreate,
            include=lambda request, **_: request.user.is_staff,
        ),

        detail=M(
            display_name=lambda load_function, **_: load_function.name,
            open=True,
            params={'load_function'},
            path='<load_function>/',
            url=lambda load_function, **_: f"/{LoadFunction.url_root}/{load_function.pk}/",
            view=LoadFunctionDetail,

            items=dict(
                edit=M(
                    icon=settings.ICON_EDIT,
                    view=LoadFunctionEdit,
                    include=lambda request, **_: request.user.is_staff,
                ),
                delete=M(
                    icon=settings.ICON_DELETE,
                    view=LoadFunctionDelete,
                    include=lambda request, **_: request.user.is_staff,
                ),
                # history=M(
                #     icon='clock-rotate-left',
                #     view=LoadFunctionHistory
                # )
            ),
        ),
    ),
)
