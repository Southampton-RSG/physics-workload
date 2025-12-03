"""
Handles the URLs for the Standard Load
"""

from iommi.main_menu import M
from iommi.path import register_path_decoding

from app.models.standard_load import StandardLoad
from app.pages.standard_load import StandardLoadDetail, StandardLoadEdit, StandardLoadList, StandardLoadNewYear

# Decode <standard_load> in paths so a StandardLoad object is in the view parameters.
register_path_decoding(standard_load=StandardLoad)


# Included in the main menu
standard_load_submenu: M = M(
    icon=StandardLoad.icon,
    include=lambda user, **_: user.is_authenticated,
    view=StandardLoadList().as_view(),
    items=dict(
        detail=M(
            display_name=lambda standard_load, **_: standard_load,
            include=lambda user, **_: user.has_perm("app.view_standardload"),
            params={"standard_load"},
            path="<standard_load>/",
            url=lambda standard_load, **_: standard_load.get_absolute_url(),
            view=StandardLoadDetail().as_view(),
            items=dict(
                edit=M(
                    icon="pencil",
                    include=lambda user, standard_load, **_: user.has_perm("change_standardload", standard_load),
                    view=StandardLoadEdit().as_view(),
                ),
                create=M(
                    display_name="New Year",
                    icon="plus",
                    include=lambda user, standard_load, **_: user.has_perm("add_standardload", standard_load),
                    view=StandardLoadNewYear().as_view(),
                ),
            ),
        ),
    ),
)
