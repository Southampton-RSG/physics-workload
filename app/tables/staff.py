from django.db.models import Q

from iommi import Table, Column, Field, Action

from app.models.staff import Staff
from app.pages import ColumnModify
from app.style import floating_fields_style


class StaffTable(Table):
    class Meta:
        auto__model=Staff
        auto__include=[
            'account', 'name', 'gender', 'academic_group', 'is_active',
            'load_calculated_balance', 'load_historic_balance', 'assignment_set',
        ]
        columns__name__cell__url=lambda row, **_: row.get_absolute_url()
        columns__name__filter__include=True
        columns__account__cell__url=lambda row, **_: row.get_absolute_url()
        columns__academic_group=dict(
            # Invisible but used for filtering
            filter__include=True,
            render_column=False,
        )
        columns__academic_group_code=Column(
            # Invisible column that's just here to pull data through from the unit for rendering
            attr='academic_group__code',
            after='name',
            display_name="Group",
            cell__url=lambda row, **_: row.academic_group.get_absolute_url(),
        )
        columns__gender=dict(
            filter__include=True,
            render_column=False,
        )
        columns__assignment_set=dict(
            cell__template='app/staff/assignment_set.html',
        )
        columns__is_active=dict(
            render_column=False,
            # filter__include=True,
        )
        columns__load_historic_balance=dict(
            group="Load Balance",
            display_name='Historic',
            cell__template='app/integer_cell.html',
        )
        columns__load_calculated_balance=dict(
            group="Load Balance",
            display_name='Current',
            cell__template='app/integer_cell.html',
        )
        columns__modify=ColumnModify.create()
        query=dict(
            advanced__include=False,
            form=dict(
                fields__status=Field.choice(
                    display_name='Status',
                    choices=lambda params, **_: [
                        '---', 'Underloaded', 'Overloaded'
                    ],
                ),
                fields__gender=Field.choice(
                    display_name='Gender',
                    choices=lambda params, **_: [''] + list(set(Staff.objects.values_list('gender', flat=True))),
                    after='academic_group',
                ),
                # fields__is_active=Field.boolean(
                #     display_name='Active Only',
                #     initial=True,
                #     iommi_style='boolean_buttons',
                #     after='load_calculated_balance',
                # ),
                actions__reset=Action.button(display_name='Clear Filter', attrs__type='reset'),
            ),
            filters=dict(
                status__value_to_q=lambda value_string_or_f, **_: StaffTable.filter_status_into_query(
                    value_string_or_f)
            ),
        )
        iommi_style=floating_fields_style

    @staticmethod
    def filter_status_into_query(value_string_or_f) -> Q|None:
        if value_string_or_f == 'Underloaded':
            return Q(load_calculated_balance__gt=0)
        elif value_string_or_f == 'Overloaded':
            return Q(load_calculated_balance__lt=0)
        else:
            return Q()
