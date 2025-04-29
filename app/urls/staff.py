from iommi.path import register_path_decoding
from iommi.experimental.main_menu import M

from dash_bootstrap_templates import load_figure_template
load_figure_template('bootstrap_dark')

from app.auth import has_access_decoder
from app.models.staff import Staff
from app.pages.staff import StaffEdit, StaffDelete, StaffList, StaffDetail, StaffHistoryDetail, StaffHistoryList, StaffCreate


register_path_decoding(
    staff=has_access_decoder(Staff, "You may only view your own Staff details."),
)
register_path_decoding(
    staff_history=lambda string, **_: Staff.history.get(history_id=int(string)),
)

staff_submenu: M = M(
    icon=Staff.icon,
    view=StaffList,
    include=lambda request, **_: request.user.is_authenticated,
    items=dict(
        create=M(
            icon="plus",
            include=lambda request, **_: request.user.is_staff,
            view=StaffCreate,
        ),
        detail=M(
            display_name=lambda staff, **_: staff.name,
            open=True,
            params={'staff'},
            path='<staff>/',
            url=lambda staff, **_: f"/{Staff.url_root}/{staff.account}/",
            view=StaffDetail,

            items=dict(
                edit=M(
                    icon='pencil',
                    view=StaffEdit,
                    include=lambda request, **_: request.user.is_staff,
                ),
                delete=M(
                    icon='trash',
                    view=StaffDelete,
                    include=lambda request, **_: request.user.is_staff,
                ),
                history=M(
                    icon='clock-rotate-left',
                    view=StaffHistoryList,
                    items=dict(
                        detail=M(
                            display_name=lambda staff_history, **_: staff_history.history_date.date(),
                            params={'staff_history'},
                            path='<staff_history>/',
                            view = StaffHistoryDetail,
                        )
                    )
                ),
            ),
        ),
    )
)