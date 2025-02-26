"""
Handles the views for the Academic Groups
"""
from django.urls import path
from django.utils.html import format_html
from django.template import Template

from iommi import Page, Table, html, Form, EditTable, Column
from iommi.path import register_path_decoding
from iommi import register_search_fields
from iommi.views import crud_views

from app.pages import BasePage
from app.models import Staff, Assignment


register_path_decoding(
    staff=lambda string, **_: Staff.objects.get(account=string)
)
register_search_fields(
    model=Staff, search_fields=['name', 'gender', 'academic_group'], allow_non_unique=True
)


class StaffDetail(BasePage):
    """

    """
    title = html.h1(lambda params, **_: f"{params.staff}")
    detail_table = Table(
        title=None,
        auto__model=Staff,
        auto__include=['account', 'name', 'gender', 'type', 'academic_group'],
        rows=lambda params, **_: [params.staff],
        sortable=False,
    )
    load_table = Table(
        title=None,
        auto__model=Staff,
        auto__include=[
            'load_calculated_target',
            'load_calculated_assigned',
            'load_calculated_balance',
            'load_historic_balance',
        ],
        columns__fte_fraction__include=lambda params, **_: params.staff.fte_fraction,
        columns__hours_fixed__include=lambda params, **_: params.staff.hours_fixed,
        # columns__load_balance_current=Column(
        #     display_name="Current load balance",
        #     cell__value=lambda params, **_: params.staff.load_calculated_target - params.staff.load_calculated_actual,
        #     sortable=False,
        # ),
        # columns__load_balance__after="load_balance_current",
        rows=lambda params, **_: [params.staff],
        sortable=False,
    )
    # form = Form(
    #     auto__model=Staff,
    #     auto__exclude=['user', 'is_active'],
    #     fields__account__group='row1',
    #     fields__academic_group__group='row1',
    #     fields__name__group='row1',
    #     instance=lambda params, **_: params.staff,
    #     editable=False,
    # )
    assignments = Table(
        auto__model=Assignment,
        auto__exclude=['notes'],
        rows=lambda params, **_: Assignment.objects.filter(staff=params.staff),
    )

#     table_staff = Table(
#         auto__model=Staff, auto__exclude=['user', 'notes', 'is_active'],
#         columns__name__cell__url=lambda row, **_: Staff.objects.get(pk=row.pk).get_absolute_url(),
#         rows=lambda params, **_: Staff.objects_active.filter(academic_group=params.academic_group)
#     )


class StaffList(BasePage):
    """
    List of all currently active staff.
    """
    groups = Table(
        auto__model=Staff,
        auto__include=[
            'account', 'name', 'gender', 'academic_group', 'load_calculated_balance', 'load_historic_balance'
        ],
        columns__name__cell__url=lambda row, **_: row.get_absolute_url(),
        columns__name__filter__include=True,
        columns__account__cell__url=lambda row, **_: row.get_absolute_url(),
        columns__academic_group__filter__include=True,
        columns__gender__filter__include=True,
        columns__assignment=Column(
            display_name="Assignments", sortable=False,
            cell__value=lambda row, **_: row.assignment_set.count(),
        ),
        query_from_indexes=True,
        query__advanced__include=False,
    )


urlpatterns = [
    path('staff/<staff>/edit/', StaffDetail().as_view(), name='staff_edit'),
    path('staff/<staff>/', StaffDetail().as_view(), name='staff_detail'),
    path('staff/', StaffList().as_view(), name='staff_list'),
]
