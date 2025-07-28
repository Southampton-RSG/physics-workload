"""
Paths to edit the info text that appears on some pages,
plus the way you get to the 'main' about page as a logged-in user.
"""
from typing import List
from django.conf import settings
from django.urls import path, URLPattern

from iommi.experimental.main_menu import M
from iommi.path import register_path_decoding

from app.auth import has_access_decoder
from app.models.info import Info
from app.pages.info import InfoEdit
from app.pages.basic import AboutPage


# Decode <task> in paths so a LoadFunction object is in the view parameters.
register_path_decoding(
    info=has_access_decoder(Info, "You must be Staff to edit Info items."),
)

# This is imported into the main menu tree.
info_submenu: M = M(
    icon=Info.icon,
    include=lambda user, **_: user.is_authenticated,
    view=AboutPage,
    items=dict(
        detail=M(
            display_name=lambda info, **_: info.name,
            params={'info'},
            path='<info>/',
            url=lambda info, **_: f"/{Info.url_root}/{info.page}/",
            view=InfoEdit,

            items=dict(
                edit=M(
                    icon=settings.ICON_EDIT,
                    view=InfoEdit,
                    include=lambda request, **_: request.user.is_staff,
                ),
            ),
        )
    )
)
