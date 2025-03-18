"""
Handles the views for the Academic Groups
"""
from django.urls import path
from django.db.models import F

from iommi import EditTable, EditColumn, Page, Field

from app.pages.components.headers import HeaderInstanceEdit, HeaderInstanceCreate, HeaderInstanceDelete, \
    HeaderInstanceDetail, HeaderList
from app.models import Staff, Assignment
from app.models.standard_load import get_current_standard_load
from app.forms.staff import StaffForm
from app.style import floating_fields_select2_inline_style
from app.tables.staff import StaffTable


class StaffDelete(Page):
    """

    """
    header = HeaderInstanceDelete(
        lambda params, **_: params.staff.get_instance_header()
    )
    form = StaffForm.delete(
        h_tag=None,
        instance=lambda params, **_: params.staff,
        auto__exclude=[
            'load_target', 'load_assigned', 'load_historic_balance', 'standard_load'
        ],
    )


class StaffEdit(Page):
    """

    """
    header = HeaderInstanceEdit(
        lambda params, **_: params.staff.get_instance_header()
    )
    form = StaffForm.edit(
        h_tag=None,
        auto__instance=lambda params, **_: params.staff,
        auto__exclude=['load_target', 'load_assigned', 'load_historic_balance', 'standard_load'],
        # fields__load_target__include=False,
        # fields__load_assigned__include=False,
        # fields__load_historic_balance__include=False,
        # fields__standard_load__include=False,
    )


class StaffCreate(Page):
    """

    """
    header = HeaderInstanceCreate(
        lambda params, **_: Staff.get_model_header()
    )
    form = StaffForm.create(
        h_tag=None,
        fields__standard_load=Field.non_rendered(
            include=True,
            initial=lambda params, **_: get_current_standard_load(),
        )
    )


class StaffDetail(Page):
    """
    View showing the detail of a staff member
    """
    header = HeaderInstanceDetail(
        lambda params, **_: params.staff.get_instance_header()
    )
    form = StaffForm(
        h_tag=None,
        auto__instance=lambda params, **_: params.staff,
        auto__exclude=[
            'is_active', 'notes', 'standard_load', 'user'
        ],
        fields__fte_fraction__include=lambda params, **_: params.staff.fte_fraction,
        fields__hours_fixed__include=lambda params, **_: params.staff.hours_fixed,
        fields__notes__include=lambda request, **_: request.user.is_staff,
        fields__load_target__group='row2',
        fields__load_assigned__group = 'row2',
        fields__load_historic_balance__group = 'row2',
        fields__is_active__include=False,
        editable=False,
        actions__submit=None,
    )
    assignments = EditTable(
        auto__model=Assignment,
        auto__exclude=['notes', 'load_calc',],
        columns__task__field__include=True,
        columns__is_first_time__field__include=True,
        columns__is_provisional__field__include=True,
        columns__staff=EditColumn.hardcoded(
            render_column=False,
            field__parsed_data=lambda params, **_: params.staff,
        ),
        rows=lambda params, **_: Assignment.objects.filter(staff=params.staff),
        columns__delete=EditColumn.delete(),
        iommi_style=floating_fields_select2_inline_style,
    )


class StaffList(Page):
    """
    List of all currently active staff.
    """
    header = HeaderList(
        lambda params, **_: Staff.get_model_header()
    )
    list = StaffTable(
        h_tag=None,
        rows=StaffTable.annotate_rows(Staff.objects_active),
    )


urlpatterns = [
    path('staff/create/', StaffCreate().as_view(), name='staff_create'),
    path('staff/<staff>/delete/', StaffDelete().as_view(), name='staff_delete'),
    path('staff/<staff>/edit/', StaffEdit().as_view(), name='staff_edit'),
    path('staff/<staff>/', StaffDetail().as_view(), name='staff_detail'),
    path('staff/', StaffList().as_view(), name='staff_list'),
]
