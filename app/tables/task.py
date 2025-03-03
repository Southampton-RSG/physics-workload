from django.contrib.admin import display
from django.db.models import Q, QuerySet, F, Count

from iommi import Table, Column, Field, Style, Asset

from app.pages import create_modify_column
from app.models import Task
from app.style import floating_fields_style, floating_fields


class TaskTable(Table):
    class Meta:
        h_tag=None
        auto__model=Task
        auto__include=[
            'unit', 'name', 'number_needed', 'students',
            'load_calc', 'load_calc_first', 'assignment_set'
        ]
        columns__name=dict(
            after='unit',
            cell__url=lambda row, **_: row.get_absolute_url(),
            filter=dict(
                include=True,
                freetext=True,
            )
        )
        columns__unit=dict(
            cell__url=lambda row, **_: row.unit.get_absolute_url() if row.unit else '',
            auto_rowspan=True,
        )
        columns__unit_name=Column(
            # Invisible column that's just here to pull data through from the unit for rendering
            attr='unit__name',
            render_column=False,
            filter=dict(
                include=True,
                freetext=True,
            )
        )
        columns__number_needed=dict(
            group='Assignments',
            display_name='Required'
        )
        columns__assignment_open=dict(
            group="Assignments",
            display_name="Open",
            after="number_needed",
            sortable=True,
        )
        columns__assignment_set=dict(
            cell__template='app/unit/assignment_set.html',
            group="Assignments",
            display_name='',
            after='assignment_open',
        )
        columns__load_calc=dict(
            group='Load',
            display_name='Normal',
        )
        columns__load_calc_first=dict(
            group='Load',
            display_name='First time',
        )
        columns__is_active=dict(
            render_column=False,
            filter__include=True,
        )
        columns__modify=create_modify_column()
        query=dict(
            advanced__include=False,
            form=dict(
                fields__has_any_provisional=Field.boolean(
                    display_name='Has Provisional Assignments',
                    iommi_style='boolean_buttons',
                ),
                fields__is_active=Field.boolean(
                    display_name='Active Only',
                    initial=True,
                    iommi_style='boolean_buttons',
                )
            ),
            # TODO: Fix, this doesn't work as the provisional counting doesn't work yet
            filters__has_any_provisional__value_to_q=lambda value_string_or_f, **_: Q(assignment_set__gt=0 if value_string_or_f=='1' else 0),
        )
        page_size=50
        iommi_style=floating_fields_style
        empty_message = "No tasks available."

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
        )
