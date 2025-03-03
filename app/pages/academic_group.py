"""
Handles the views for the Academic Groups
"""
from django.db.models import Count, Sum
from django.urls import path
from django.utils.html import format_html, mark_safe
from django.template import Template

from iommi import Page, Table, html, Form, EditTable, Column, Action, Menu, Fragment
from iommi.path import register_path_decoding

from app.models import AcademicGroup, Staff, Unit, Task
from app.pages import BasePage, HeaderInstanceDetail, HeaderList, HeaderInstanceEdit, HeaderInstanceCreate, HeaderInstanceDelete


register_path_decoding(academic_group=lambda string, **_: AcademicGroup.objects.get(code=string))


class AcademicGroupDetail(BasePage):
    """
    Detail view showing group members and their workloads,
    as well as any units and their assignment status.
    """
    header = HeaderInstanceDetail(
        lambda params, **_: format_html(
            params.academic_group.get_instance_header()
        ),
    )

    staff = Table(
        auto__model=Staff,
        auto__include=[
            'name', 'load_calculated_target', 'load_calculated_assigned', 'load_calculated_balance',
            'load_historic_balance', 'assignment_set'
        ],
        columns__load_calculated_assigned=dict(
            display_name='Assigned',
            group='Current year load',
        ),
        columns__load_calculated_target=dict(
            display_name='Target',
            group='Current year load',
        ),
        columns__load_calculated_balance=dict(
            display_name='Balance',
            group='Current year load',
        ),
        columns__assignment_set={
            "cell__template": 'app/academic_group/assignment_set.html',
        },
        rows=lambda params, **_: Staff.objects_active.filter(academic_group=params.academic_group),
        columns__name__cell__url = lambda row, **_: row.get_absolute_url(),
        page_size=20,
        h_tag__tag='h2',
    )
    units = Table(
        auto__model=Unit,
        auto__include=['code', 'name', 'task_set', 'students'],
        columns__code__cell__url=lambda row, **_: row.get_absolute_url(),
        columns__name__cell__url=lambda row, **_: row.get_absolute_url(),
        columns__task_set=dict(
            display_name='Tasks',
            cell__template='app/list_cell_name.html',
            after='students',
        ),
        rows=lambda params, **_: Unit.objects_active.filter(
            academic_group=params.academic_group
        ),
        page_size=20,
        h_tag__tag='h2',
    )


class AcademicGroupEdit(BasePage):
    """
    Page showing an academic group to be edited
    """
    header = HeaderInstanceEdit(
        lambda params, **_: format_html(params.academic_group.get_instance_header()),
    )
    form = Form.edit(
        h_tag=None,
        auto__model=AcademicGroup, instance=lambda params, **_: params.academic_group,
        fields__code__group="row1",
        fields__name__group="row1",
        extra__redirect_to='..',
    )


class AcademicGroupCreate(BasePage):
    """
    Page showing an academic group to be created
    """
    header = HeaderInstanceCreate(
        lambda params, **_: format_html(AcademicGroup.get_model_header()),
    )
    form = Form.create(
        h_tag=None,
        auto__model=AcademicGroup,
        fields__code__group="row1",
        fields__name__group="row1",
    )


class AcademicGroupDelete(BasePage):
    """
    Page showing an academic group to be created
    """
    header = HeaderInstanceDelete(
        lambda params, **_: format_html(params.academic_group.get_instance_header()),
    )
    warning = html.p(
        "If this group has been used, edit it and remove the 'active' flag instead."
    )
    form = Form.delete(
        h_tag=None,
        auto__model=AcademicGroup, instance=lambda params, **_: params.academic_group,
        fields__code__group="row1",
        fields__name__group="row1",
    )



class AcademicGroupList(BasePage):
    """
    Page listing the academic groups
    """
    title = HeaderList(
        lambda params, **_: format_html(
            AcademicGroup.get_model_header(),
        ),
    )
    list = Table(
        h_tag=None,
        auto__model=AcademicGroup,
        auto__include=['name'],
        columns__staff=Column(
            cell__value=lambda row, **_: row.staff_set.count(),
        ),
        columns__units=Column(
            cell__value=lambda row, **_: row.unit_set.count(),
        ),
        columns__name__cell__url=lambda row, **_: row.get_absolute_url(),
        columns__edit=Column.edit(
            cell__url=lambda row, **_: f"{row.get_absolute_url()}edit/",
            include=lambda request, **_: request.user.is_staff,
        ),
    )


urlpatterns = [
    path('group/create/', AcademicGroupCreate().as_view(), name='academic_group_create'),
    path('group/<academic_group>/edit/', AcademicGroupEdit().as_view(), name='academic_group_edit'),
    path('group/<academic_group>/delete/', AcademicGroupDelete().as_view(), name='academic_group_edit'),
    path('group/<academic_group>/', AcademicGroupDetail().as_view(), name='academic_group_detail'),
    path('group/', AcademicGroupList().as_view(), name='academic_group_list'),
]
