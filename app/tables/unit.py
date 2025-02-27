from django.db.models import Q, Sum, Count
from django.db.models import QuerySet, Manager
from iommi import Table, Column, Field

from app.models import Unit



class UnitTable(Table):
    class Meta:
        auto__model=Unit,
        auto__include=['code', 'name', 'academic_group', 'task_set', 'students'],
        columns__code=dict(
            cell__url=lambda row, **_: row.get_absolute_url(),
            filter__include=True,
        ),
        columns__name=dict(
            cell__url=lambda row, **_: row.get_absolute_url(),
            filter__include=True,
        ),
        columns__task_open=Column(
            display_name='Tasks',
            filter__include=True,
            after='students',
        ),
        columns__task_set=dict(
            display_name='',
            cell__template='app/list_cell_name.html',
            after='task_open',
        ),
        query__form__fields__task_open=Field.number(
            display_name='Open Tasks'
        ),
        query__filters__task_open__value_to_q=lambda value_string_or_f, **_: Q(task_open__gte=int(value_string_or_f)),
        query__form__fields__task_provisional=Field.boolean(
            display_name='Provisional Assignments',
            iommi_style='boolean_buttons',
        ),
        query__filters__task_provisional__value_to_q=lambda value_string_or_f, **_: Q(task_provisional__gte=1 if value_string_or_f=='1' else 0),

        #
        # rows=lambda params, **_: Unit.objects_active.annotate(
        #     assignment_count=Count('task_set__assignment_set'),
        #     task_count=Sum('task_set__number_needed'),
        #     task_open=Sum('task_set__number_needed')-Count('task_set__assignment_set'),
        #     task_provisional=Count('task_set__assignment_set__is_provisional'),
        # ),
        page_size=20,
        h_tag=None,
        query__advanced__include=False,
