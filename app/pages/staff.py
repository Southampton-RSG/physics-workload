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

from app.models import Staff, StaffYear, Assignment


register_path_decoding(staff=lambda string, **_: Staff.objects.get(account=string))


class StaffPage(Page):
    """

    """
    title = html.h1(lambda params, **_: f"{params.staff}")
    form = Form(
        auto__model=Staff,
        auto__exclude=['user', 'is_active'],
        fields__account__group='row1',
        fields__academic_group__group='row1',
        fields__name__group='row1',
        instance=lambda params, **_: params.staff,
        editable=False,
    )
    assignments = Table(
        auto__model=Assignment,
        rows=lambda params, **_: Assignment.objects.filter(staff_year=params.staff.staffyear_set.latest()),
    )

    staff_years = Table(
        auto__model=StaffYear,
        auto__exclude=['notes'],
        rows=lambda params, **_: StaffYear.objects.filter(staff=params.staff),
        columns__load_balance=Column(

        )
    )

#     table_staff = Table(
#         auto__model=Staff, auto__exclude=['user', 'notes', 'is_active'],
#         columns__name__cell__url=lambda row, **_: Staff.objects.get(pk=row.pk).get_absolute_url(),
#         rows=lambda params, **_: Staff.objects_active.filter(academic_group=params.academic_group)
#     )


urlpatterns = [
    path('staff/<staff>/', StaffPage().as_view(), name='staff_detail'),
    path('staff/', crud_views(model=Staff)),
]
