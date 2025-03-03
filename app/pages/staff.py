"""
Handles the views for the Academic Groups
"""
from django.urls import path

from iommi import Table, Column, Action, Field
from iommi.path import register_path_decoding

from app.pages import BasePage, HeaderInstanceDetail, HeaderInstanceEdit, HeaderInstanceCreate, HeaderInstanceDelete, HeaderList, create_modify_column
from app.models import Staff, Assignment
from app.style import floating_fields_style, boolean_button_fields_style
from app.forms.staff import StaffForm

register_path_decoding(
    staff=lambda string, **_: Staff.objects.get(account=string)
)
# register_search_fields(
#     model=Staff, search_fields=['name', 'gender', 'academic_group'], allow_non_unique=True
#)


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
        instance=lambda params, **_: params.staff,
        fields__is_active__include=True,
    )


class StaffDetail(BasePage):
    """

    """
    header = HeaderInstanceDetail(
        lambda params, **_: params.staff.get_instance_header()
    )
    form = StaffForm(
        h_tag=None,
        instance=lambda params, **_: params.staff,
        iommi_style=floating_fields_style,
        editable=False,
    )
    assignments = Table(
        auto__model=Assignment,
        auto__exclude=['notes'],
        rows=lambda params, **_: Assignment.objects.filter(staff=params.staff),
    )



class StaffList(BasePage):
    """
    List of all currently active staff.
    """
    header = HeaderList(
        lambda params, **_: Staff.get_model_header()
    )
    list = Table(
        h_tag=None,
        auto__model=Staff,
        auto__include=[
            'account', 'name', 'gender', 'academic_group', 'load_calculated_balance', 'load_historic_balance'
        ],
        columns__name__cell__url=lambda row, **_: row.get_absolute_url(),
        columns__name__filter__include=True,
        columns__account__cell__url=lambda row, **_: row.get_absolute_url(),
        columns__academic_group__filter__include=True,
        columns__gender__filter__include=True,
        columns__gender__render_column=False,
        columns__assignment=Column(
            display_name="Assignments", sortable=False,
            cell__value=lambda row, **_: row.assignment_set.count(),
        ),
        columns__modify=create_modify_column(),
        query=dict(
            advanced__include=False,
            form=dict(
                fields__gender=Field.choice(
                    display_name='Gender',
                    choices=lambda params, **_: ['']+list(set(Staff.objects.values_list('gender', flat=True)))
                ),
                actions__reset=Action.button(display_name='Clear Filter', attrs__type='reset'),
            ),
        ),
        iommi_style=floating_fields_style,
    )


urlpatterns = [
    path('staff/<staff>/delete/', StaffDelete().as_view(), name='staff_delete'),
    path('staff/<staff>/edit/', StaffEdit().as_view(), name='staff_edit'),
    path('staff/<staff>/', StaffDetail().as_view(), name='staff_detail'),
    path('staff/', StaffList().as_view(), name='staff_list'),
]
