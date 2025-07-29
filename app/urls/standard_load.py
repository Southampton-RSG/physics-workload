"""
Handles the URLs for the Standard Load
"""

from iommi.experimental.main_menu import M
from iommi.path import register_path_decoding

from app.models.standard_load import StandardLoad
from app.pages.standard_load import StandardLoadDetail, StandardLoadEdit, StandardLoadList, StandardLoadNewYear

# Decode <standard_load> in paths so a StandardLoad object is in the view parameters.
register_path_decoding(standard_load=lambda string, **_: StandardLoad.objects.get(year=int(string)))


# Included in the main menu
standard_load_submenu: M = M(
    icon=StandardLoad.icon,
    include=lambda request, **_: request.user.is_authenticated,
    view=StandardLoadList,
    items=dict(
        detail=M(
            display_name=lambda standard_load, **_: standard_load,
            open=True,
            params={"standard_load"},
            path="<standard_load>/",
            url=lambda standard_load, **_: standard_load.get_absolute_url(),
            view=StandardLoadDetail,
            items=dict(
                edit=M(
                    icon="pencil",
                    include=lambda request, standard_load, **_: request.user.is_staff and (StandardLoad.objects.latest() == standard_load),
                    view=StandardLoadEdit,
                ),
                create=M(
                    display_name="New Year",
                    icon="plus",
                    include=lambda request, standard_load, **_: request.user.is_staff and (StandardLoad.objects.latest() == standard_load),
                    view=StandardLoadNewYear,
                ),
            ),
        ),
    ),
)
