"""
Handles the views for the Academic Groups
"""
from django.urls import path

from iommi import Table, Column, Action, Field, EditTable, EditColumn
from iommi.path import register_path_decoding

from app.pages import BasePage, ColumnModify
from app.pages.components.headers import HeaderInstanceEdit, HeaderInstanceCreate, HeaderInstanceDelete, \
    HeaderInstanceDetail, HeaderList
from app.models import Staff, Assignment, AcademicGroup
from app.style import floating_fields_style, boolean_button_fields_style
from app.forms.staff import StaffForm
from app.tables.staff import StaffTable


register_path_decoding(
    staff=lambda string, **_: Staff.objects.get(account=string)
)


class StaffDelete(BasePage):
    """

    """
    header = HeaderInstanceDelete(
        lambda params, **_: params.staff.get_instance_header()
    )
    form = StaffForm.delete(
        h_tag=None,
        instance=lambda params, **_: params.staff,
        fields__is_active__include=True,
    )


class StaffEdit(BasePage):
    """

    """
    header = HeaderInstanceEdit(
        lambda params, **_: params.staff.get_instance_header()
    )
    form = StaffForm.edit(
        h_tag=None,
        auto__instance=lambda params, **_: params.staff,
        fields__is_active__include=True,
    )


class StaffCreate(BasePage):
    """

    """
    header = HeaderInstanceCreate(
        lambda params, **_: Staff.get_model_header()
    )
    form = StaffForm.create(
        h_tag=None,
    )


class StaffDetail(BasePage):
    """

    """
    header = HeaderInstanceDetail(
        lambda params, **_: params.staff.get_instance_header()
    )
    form = StaffForm(
        h_tag=None,
        auto__instance=lambda params, **_: params.staff,
        fields__hours_fixed__include=lambda params, **_: params.staff.hours_fixed,
        fields__fte_fraction__include = lambda params, **_: params.staff.fte_fraction,
        editable=False,
    )
    assignments = EditTable(
        auto__model=Assignment,
        auto__exclude=['notes'],
        columns__task__field__include=True,
        columns__is_first_time__field__include=True,
        columns__is_provisional__field__include=True,
        columns__staff=EditColumn.hardcoded(
            render_column=False,
            field__parsed_data=lambda params, **_: params.staff,
        ),
        rows=lambda params, **_: Assignment.objects.filter(staff=params.staff),
        columns__delete=EditColumn.delete(),
    )


class StaffList(BasePage):
    """
    List of all currently active staff.
    """
    header = HeaderList(
        lambda params, **_: Staff.get_model_header()
    )
    list = StaffTable(
        h_tag=None,
    )


urlpatterns = [
    path('staff/create/', StaffCreate().as_view(), name='staff_create'),
    path('staff/<staff>/delete/', StaffDelete().as_view(), name='staff_delete'),
    path('staff/<staff>/edit/', StaffEdit().as_view(), name='staff_edit'),
    path('staff/<staff>/', StaffDetail().as_view(), name='staff_detail'),
    path('staff/', StaffList().as_view(), name='staff_list'),
]
