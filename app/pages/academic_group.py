"""
Handles the views for the Academic Groups
"""
from django.db.models import Count, Sum, Q, F
from django.urls import path

from iommi import Page, Table, html, Form, EditTable, Column, Action, Menu, Fragment, Header

from app.models import AcademicGroup, Staff, Unit
from app.tables.staff import StaffTable
from app.pages.components.headers import HeaderInstanceEdit, HeaderInstanceCreate, HeaderInstanceDelete, \
    HeaderInstanceDetail, HeaderList


class AcademicGroupDetail(Page):
    """
    Detail view showing group members and their workloads,
    as well as any units and their assignment status.
    """
    header = Header(
        lambda params, **_: params.academic_group.get_instance_header()
    )

    staff = StaffTable(
        rows=lambda params, **_: StaffTable.annotate_rows(params.academic_group.staff_set.filter(is_removed=False)),
        columns__academic_group_code__include=False,
        query__include=False,
        attrs__class={'mb-3': True},
    )
    units = Table(
        auto__model=Unit,
        auto__include=['code', 'name', 'task_set', 'students'],
        columns__code__cell__url=lambda row, **_: row.get_absolute_url(),
        columns__name__cell__url=lambda row, **_: row.get_absolute_url(),
        columns__task_set=dict(
            display_name="Tasks",
            cell__template='app/academic_group/task_set.html',
            after='students',
        ),
        rows=lambda params, **_: Unit.objects.filter(
            academic_group=params.academic_group
        ).annotate(
            assignment_open=Sum('task_set__number_needed') - Count('task_set__assignment_set'),
        ),
        page_size=20,
        h_tag__tag='h2',
        empty_message="No units available.",
    )


class AcademicGroupEdit(Page):
    """
    Page showing an academic group to be edited
    """
    header = Header(
        lambda params, **_: params.academic_group.get_instance_header()
    )
    form = Form.edit(
        h_tag=None,
        auto__model=AcademicGroup, instance=lambda params, **_: params.academic_group,
        fields__code__group='row1',
        fields__short_name__group='row1',
        fields__name__group='row1',
        extra__redirect_to='..',
    )


class AcademicGroupCreate(Page):
    """
    Page showing an academic group to be created
    """
    header = Header(
        lambda params, **_: AcademicGroup.get_model_header_singular()
    )
    form = Form.create(
        h_tag=None,
        auto__model=AcademicGroup,
        fields__code__group='row1',
        fields__short_name__group='row1',
        fields__name__group='row1',
    )


class AcademicGroupDelete(Page):
    """
    Page showing an academic group to be created
    """
    header = Header(
        lambda params, **_: params.academic_group.get_instance_header(),
    )
    warning = html.p(
        "If this group has been used, edit it and remove the 'active' flag instead."
    )
    form = Form.delete(
        h_tag=None,
        auto__model=AcademicGroup, instance=lambda params, **_: params.academic_group,
        fields__code__group='row1',
        fields__short_name__group='row1',
        fields__name__group='row1',
    )


class AcademicGroupList(Page):
    """
    Page listing the academic groups
    """
    title = Header(
        lambda params, **_: AcademicGroup.get_model_header(),
    )
    list = Table(
        h_tag=None,
        auto__model=AcademicGroup,
        rows=AcademicGroup.available_objects.all(),
        auto__include=['name'],
        columns__staff=Column(
            cell__value=lambda row, **_: row.staff_set.filter(is_removed=False).count(),
        ),
        columns__units=Column(
            cell__value=lambda row, **_: row.unit_set.filter(is_removed=False).count(),
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
