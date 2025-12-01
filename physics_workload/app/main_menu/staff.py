from django.conf import settings
from iommi.main_menu import M
from iommi.path import register_path_decoding

from app.models.staff import Staff
from app.pages.staff import StaffCreate, StaffDelete, StaffDetail, StaffEdit, StaffList
from app.pages.staff.history import StaffHistoryDetail, StaffHistoryList

register_path_decoding(staff=Staff)
register_path_decoding(
    staff_history=lambda string, **_: Staff.history.get(history_id=int(string)),
)

staff_submenu: M = M(
    icon=Staff.icon,
    view=StaffList().as_view(),
    include=lambda user, **_: user.is_authenticated,
    items=dict(
        create=M(
            icon=settings.ICON_CREATE,
            include=lambda user, **_: user.has_perm("app.add_staff"),
            view=StaffCreate().as_view(),
        ),
        detail=M(
            display_name=lambda staff, **_: staff.name,
            include=lambda user, staff, **_: user.has_perm("app.view_staff", staff),
            params={"staff"},
            path="<staff>/",
            url=lambda staff, **_: staff.get_absolute_url(),
            view=StaffDetail().as_view(),
            items=dict(
                edit=M(
                    icon=settings.ICON_EDIT,
                    include=lambda user, staff, **_: user.has_perm("app.change_staff", staff),
                    view=StaffEdit().as_view(),
                ),
                delete=M(
                    icon=settings.ICON_DELETE,
                    include=lambda user, staff, **_: user.has_perm("app.delete_staff", staff),
                    view=StaffDelete().as_view(),
                ),
                history=M(
                    icon=settings.ICON_HISTORY,
                    # If you can view, you can view history, so no extra permissions checked
                    view=StaffHistoryList().as_view(),
                    items=dict(
                        detail=M(
                            display_name=lambda staff_history, **_: staff_history.history_date.date(),
                            params={"staff_history"},
                            path="<staff_history>/",
                            view=StaffHistoryDetail().as_view(),
                        )
                    ),
                ),
            ),
        ),
    ),
)
