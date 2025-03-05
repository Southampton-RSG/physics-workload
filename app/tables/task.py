from django.db.models import Q, QuerySet, F, Count
from django.template import Template

from iommi import Table, Column, Field, LAST

from app.pages import ColumnModify
from app.models import Task
from app.style import floating_fields_style


class TaskTable(Table):
    class Meta:
        h_tag=None
        auto__model=Task
        auto__include=[
            'name',
            'load_calc', 'load_calc_first', 'assignment_set'
        ]
        # ------- INVISIBLE COLUMNS --------
        columns__unit_name=Column(
            # Invisible column that's just here to pull data through from the unit for filtering
            attr='unit__name',
            render_column=False,
            filter=dict(
                include=True,
                freetext=True,
            )
        )
        columns__assignment_open=Column(render_column=False)
        columns__assignment_provisional=Column(render_column=False)
        columns__is_active=dict(render_column=False)
        # -------- VISIBLE COLUMNS --------
        columns__unit_code=Column(
            attr='unit__code',
            display_name="Unit",
            cell__url=lambda row, **_: row.unit.get_absolute_url() if row.unit else '',
            auto_rowspan=True,
            filter=dict(
                include=True,
                freetext=True,
            )
        )
        columns__name=dict(
            after='unit_code',
            cell__url=lambda row, **_: row.get_absolute_url(),
            filter=dict(
                include=True,
                freetext=True,
            )
        )
        columns__load_calc=dict(
            group='Load',
            display_name='Normal',
            after='name',
            cell__template='app/integer_cell.html',
        )
        columns__load_calc_first=dict(
            group='Load',
            display_name='First time',
            after='load_calc',
            cell__template='app/integer_cell.html',
        )
        columns__assignment_set=dict(
            cell__template='app/task/assignment_set.html',
            display_name='Assignment(s)',
            after='load_calc_first',
        )
        columns__modify=ColumnModify.create()
        # -------- QUERY MODIFICATIONS --------
        query=dict(
            advanced__include=False,
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
                    iommi_style='boolean_buttons',
                    after=LAST,
                )
            ),
            filters=dict(
                status__value_to_q=lambda value_string_or_f, **_: TaskTable.filter_status_into_query(value_string_or_f),
            ),
        )
        page_size=50
        iommi_style=floating_fields_style
        empty_message = "No tasks available."

    @staticmethod
    def filter_status_into_query(value_string_or_f) -> Q:
        if value_string_or_f == "Has Unassigned":
            return Q(assignment_open__gt=0)
        elif value_string_or_f == "Has Provisional":
            return Q(assignment_provisional__gt=0)
        else:
            return Q()

    @staticmethod
    def annotate_query_set(query_set: QuerySet[Task]) -> QuerySet[Task]:
        """
        Annotates the passed QuerySet with any additional data needed for columns,
        convenience method to keep consistent between uses.
        :param query_set: QuerySet to annotate.
        :return: Annotated QuerySet, with the number of assignments yet needed added as `assignment_open`
        """
        return query_set.annotate(
            assignment_open=F('number_needed') - Count('assignment_set'),
            assignment_provisional=Count('assignment_set__is_provisional'),
        )
