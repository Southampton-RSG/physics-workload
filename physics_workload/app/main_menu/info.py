"""
Paths to edit the info text that appears on some pages,
plus the way you get to the 'main' about page as a logged-in user.
"""

from django.conf import settings
from iommi.main_menu import M
from iommi.path import register_path_decoding

from app.models.info import Info
from app.pages.basic import AboutPage
from app.pages.info import InfoDetail, InfoEdit

# Decode <task> in paths so a LoadFunction object is in the view parameters.
register_path_decoding(info=Info)

# This is imported into the main menu tree.
info_submenu: M = M(
    icon=Info.icon,
    include=lambda user, **_: user.is_authenticated,
    view=AboutPage().as_view(),
    items=dict(
        detail=M(
            display_name=lambda info, **_: info.name,
            include=lambda user, **_: user.has_perm("view_info"),
            params={"info"},
            path="<info>/",
            url=lambda info, **_: f"/{Info.url_root}/{info.page}/",
            view=InfoDetail().as_view(),
            items=dict(
                edit=M(
                    icon=settings.ICON_EDIT,
                    view=InfoEdit().as_view(),
                    include=lambda user, info, **_: user.has_perm("change_info", info),
                ),
            ),
        )
    ),
)
