from django.db.models import Q, Sum, Count
from django.db.models import QuerySet, Manager
from django.utils.html import format_html
from iommi import Table, Column, Field, Action

from app.models import Unit
from app.style import floating_fields_style


class UnitTable(Table):
    class Meta:
        auto__model=Unit
        auto__include=['is_active', 'code', 'name', 'academic_group', 'task_set', 'students']
        # -------- HIDDEN COLUMNS --------
        columns__assignment_open=Column(render_column=False)
        columns__assignment_provisional=Column(render_column=False)
        # -------- VISIBLE COLUMNS ------
        columns__code=dict(
            cell__url=lambda row, **_: row.get_absolute_url(),
            filter=dict(
                include=True,
                freetext=True,
            ),
        )
        columns__name=dict(
            cell__url=lambda row, **_: row.get_absolute_url(),
            filter=dict(
                include=True,
                freetext=True,
            ),
        )
        columns__is_active=dict(
            render_column=False,
            filter__include=True,
        )
        columns__task_set=dict(
            display_name='Tasks',
            cell__template='app/unit/task_set.html',
            after='students',
            sort_key='assignment_open',
            sortable=True,
        )
        # -------- FILTER --------
        query=dict(
            advanced__include=False,
            filters=dict(
                status__value_to_q=lambda value_string_or_f, **_: UnitTable.filter_status_into_query(value_string_or_f),
            ),
            form=dict(
                fields__status=Field.choice(
                    display_name="Status",
                    choices=[
                        '---',
                        'Has Provisional',
                        'Has Unassigned',
                    ],
                ),
                fields__is_active=Field.boolean(
                    display_name='Active Only',
                    initial=True,
                    after='status',
                ),
                actions__reset=Action.button(display_name='Clear Filter', attrs__type='reset'),
            ),
        )
        page_size=20
        h_tag=None
        iommi_style=floating_fields_style

    @staticmethod
    def filter_status_into_query(value_string_or_f) -> Q:
        if value_string_or_f == "Has Unassigned":
            return Q(assignment_open__gt=0)
        elif value_string_or_f == "Has Provisional":
            return Q(assignment_provisional__gt=0)
        else:
            return Q()

    @staticmethod
    def annotate_query_set(query_set: QuerySet[Unit]) -> QuerySet[Unit]:
        return query_set.annotate(
            assignment_open=Sum('task_set__number_needed') - Count('task_set__assignment_set'),
            assignment_provisional=Count('task_set__assignment_set__is_provisional'),
        )