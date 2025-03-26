from django.conf import settings
from django.db.models import Q, QuerySet, F

from iommi import Table, Column, Field, Action

from app.models.staff import Staff
from app.pages.components.tables import ColumnModify
from app.style import floating_fields_style
from app.auth import has_staff_access


class StaffTable(Table):
    """
    Table displaying details of staff.

    Includes status filter and staff balances only if the user is allowed,
    otherwise they can only see their own balance.
    """
    class Meta:
        auto__model=Staff
        auto__include=[
            'account', 'name', 'gender', 'academic_group', 'load_historic_balance', 'assignment_set',
        ]
        columns=dict(
            name=dict(
                cell__url=lambda row, request, **_: row.get_absolute_url_authenticated(request.user),
                filter__include=True
            ),
            account=dict(
                cell__url=lambda row, request, **_: row.get_absolute_url_authenticated(request.user),
            ),
            academic_group=dict(
                # Invisible but used for filtering
                filter__include=True,
                render_column=False,
            ),
            academic_group_code=Column(
                # Invisible column that's just here to pull data through from the unit for rendering
                attr='academic_group__code',
                after='name',
                display_name="Group",
                cell__url=lambda row, request, **_: row.academic_group.get_absolute_url_authenticated(request.user),
            ),
            gender=dict(
                filter__include=True,
                render_column=False,
            ),
            assignment_set=dict(
                cell__template='app/staff/assignment_set.html',
            ),
            load_historic_balance=dict(
                group="Load Balance",
                display_name='Historic',
                cell=dict(
                    value=lambda request, row, **_: int(row.load_historic_balance) if row.has_access(request.user) else '',
                    attrs__class=lambda row, **_: {
                        'text-success': True if row.load_historic_balance > 0 else False,
                        'text-danger': True if row.load_historic_balance < 0 else False,
                    }
                )
            ),
            load_balance=dict(
                group="Load Balance",
                display_name='Current',
                cell=dict(
                    value=lambda request, row, **_: int(row.load_balance) if row.has_access(request.user) else '',
                    attrs__class=lambda row, **_: {
                        'text-success': True if row.load_balance > 0 else False,
                        'text-danger': True if row.load_balance < 0 else False,
                    }
                ),
            ),
            modify=ColumnModify.create(),
        )
        query=dict(
            advanced__include=False,
            include=lambda request, **_: has_staff_access(request.user),
            form=dict(
                fields=dict(
                    status=Field.choice(
                        display_name='Status',
                        choices=lambda params, **_: [
                            '---', 'Underloaded', 'Overloaded',
                        ],
                    ),
                    gender=Field.choice(
                        display_name='Gender',
                        choices=lambda params, **_: [''] + list(set(Staff.available_objects.values_list('gender', flat=True))),
                        after='academic_group',
                    ),
                ),
                actions__reset=Action.button(
                    display_name='Clear Filter',
                    attrs__type='reset',
                ),
            ),
            filters=dict(
                status__value_to_q=lambda value_string_or_f, **_: StaffTable.filter_status_into_query(
                    value_string_or_f
                ),
            ),
        )
        empty_message="No staff available."
        iommi_style=floating_fields_style

    @staticmethod
    def filter_status_into_query(value_string_or_f) -> Q|None:
        if value_string_or_f == 'Underloaded':
            return Q(load_balance__gt=0)
        elif value_string_or_f == 'Overloaded':
            return Q(load_balance__lt=0)
        else:
            return Q()

    @staticmethod
    def annotate_rows(rows: QuerySet) -> QuerySet:
        """
        Adds the load balance to the table rows, derived from the load columns.
        :param rows: The query to annotate.
        :return: The annotated query, with a 'load_balance' column.
        """
        return rows.annotate(load_balance=F('load_target') - F('load_assigned'))
