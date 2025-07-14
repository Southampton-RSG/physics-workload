"""
Handles the views for the Academic Groups
"""
from django.db.models import Count, Sum, F

from iommi import Page, Table, html, Form, Column, Header, Field

from app.forms.task import TaskForm
from app.models import AcademicGroup, Unit
from app.tables.task import TaskTable
from app.tables.staff import StaffTable
from app.pages.components.suffixes import SuffixCreate, SuffixEdit, SuffixDelete


class AcademicGroupTaskCreate(Page):
    """
    Create a task associated with an academic group.
    """
    header = Header(
        lambda params, **_: params.academic_group.get_instance_header(),
        children__suffix=SuffixCreate(),
    )
    form = TaskForm.create(
        h_tag=None,
        auto__exclude=[
            'load_calc', 'load_calc_first',
            'academic_group',
        ],
        fields__academic_group=Field.non_rendered(
            initial=lambda params, **_: params.academic_group,
        ),
    )


class AcademicGroupDetail(Page):
    """
    Detail view showing group members and their workloads,
    as well as any units and their assignment status.
    """
    header = Header(
        lambda params, **_: params.academic_group.get_instance_header()
    )

    staff = StaffTable(
        attrs__class={'mb-3': True},
        columns__academic_group_code__include=False,
        query__include=False,
        rows=lambda academic_group, **_: StaffTable.annotate_rows(academic_group.staff_set),
    )
    details = Table(
        auto=dict(
            model=AcademicGroup,
            include=['load_balance_historic']
        ),
        columns__load_balance=Column(
            display_name="Load Balance",
            cell__value=lambda row, **_: row.get_load_balance(),
            include=lambda request, **_: request.user.is_staff,
        ),
        rows=lambda academic_group, **_: [academic_group],
    )

    tasks = TaskTable(
        attrs__class={'mb-3': True},
        columns=dict(
            academic_group__include=False,
            unit_code__include=False,
            assignment_set__cell__template='app/academic_group/assignment_set.html',
        ),
        query__include=False,
        rows=lambda params, **_: TaskTable.annotate_query_set(params.academic_group.task_set),
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
            assignment_open=Count('task_set__is_required') - Count('task_set__assignment_set'),
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
        lambda params, **_: params.academic_group.get_instance_header(),
        children__suffix=SuffixEdit(),
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
        children__suffix=SuffixDelete(),
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
        auto=dict(
            model=AcademicGroup,
            include=['name'],
        ),
        rows=AcademicGroup.objects.all(),
        columns=dict(
            staff=Column(
                cell__value=lambda row, **_: row.staff_set.count(),
            ),
            units=Column(
                cell__value=lambda row, **_: row.unit_set.count(),
            ),
            name__cell__url=lambda row, request, **_: row.get_absolute_url_authenticated(request.user),
            load_balance_historic__include=lambda request, **_: request.user.is_staff,
            load_balance_final__include=False,
        )
    )
