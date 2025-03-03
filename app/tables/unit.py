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
        columns__task_open=Column(
            display_name='Open',
            group='Tasks',
            filter__include=True,
            after='students',
        )
        columns__task_set=dict(
            display_name='List',
            group='Tasks',
            cell__template='app/unit/task_set.html',
            after='task_open',
        )
        columns__is_active=dict(
            render_column=False,
            filter__include=True,
        )
        columns__task_provisional=Column(
            render_column=False,
        )
        query=dict(
            filters=dict(
                task_open__value_to_q=lambda value_string_or_f, **_: Q(
                    task_open__gte=int(value_string_or_f)
                ),
                task_has_any_provisional__value_to_q=lambda value_string_or_f, **_: Q(
                    task_provisional__gte=1 if value_string_or_f == '1' else 0
                ),
            ),
            form=dict(
                fields__task_open=Field.integer(
                    display_name='Open Tasks',
                    input__attrs__type='number',
                ),
                fields__task_has_any_provisional=Field.boolean(
                    display_name=format_html(
                        "Has Any Provisional <i class='fa-solid fa-clipboard-question'></i>",
                    )
                ),
                fields__is_active=Field.boolean(
                    display_name='Active Only',
                    initial=True,
                    iommi_style='boolean_buttons',
                ),
                actions__reset=Action.button(display_name='Clear Filter', attrs__type='reset'),
            ),
        )
        page_size=20
        h_tag=None
        query__advanced__include=False
        iommi_style=floating_fields_style

    @staticmethod
    def annotate_query_set(query_set: QuerySet[Unit]) -> QuerySet[Unit]:
        return query_set.annotate(
            assignment_count=Count('task_set__assignment_set'),
            task_count=Sum('task_set__number_needed'),
            task_open=Sum('task_set__number_needed') - Count('task_set__assignment_set'),
            task_provisional=Count('task_set__assignment_set__is_provisional'),
        )