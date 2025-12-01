from logging import Logger, getLogger

from django.db.models import F, Q, QuerySet
from iommi import Action, Column, Field, Table

from app.models import AcademicGroup, Assignment, Staff
from app.style import floating_fields_style, get_balance_classes

logger: Logger = getLogger(__name__)


class StaffTable(Table):
    """
    Table displaying details of staff.

    Includes status filter and staff balances only if the user is allowed,
    otherwise they can only see their own balance.
    """

    class Meta:
        auto = dict(
            model=Staff,
            include=[
                "account",
                "name",
                "gender",
                "academic_group",
                "load_balance_historic",
                "assignment_set",
            ],
        )
        columns = dict(
            account=dict(
                cell=dict(
                    url=lambda row, user, **_: row.get_absolute_url_if_permitted(user),
                    value=lambda row, **_: row.account if not row.account.startswith("unconnected") else None,
                ),
            ),
            name=dict(
                cell__url=lambda row, user, **_: row.get_absolute_url_if_permitted(user),
                filter=dict(
                    include=True,
                    freetext=True,
                ),
            ),
            academic_group=Column(
                after="name",
                cell__url=lambda row, user, **_: row.academic_group.get_absolute_url_if_permitted(user) if row.academic_group else None,
                display_name="Group",
                filter__include=True,
            ),
            gender=dict(
                filter__include=True,
                render_column=False,
            ),
            assignment_set=dict(
                cell=dict(
                    value=lambda row, **_: Assignment.objects.filter(staff=row),
                    template="app/staff/assignment_set.html",
                ),
                include=lambda user, **_: user.is_staff,
            ),
            load_balance_historic=dict(
                cell__attrs__class=lambda row, **_: get_balance_classes(row.load_balance_historic),
                display_name="Historic",
                group="Load Balance",
                include=lambda user, **_: user.is_staff,
            ),
            load_balance=dict(
                cell__attrs__class=lambda row, **_: get_balance_classes(row.load_balance),
                display_name="Current",
                group="Load Balance",
                include=lambda user, **_: user.is_staff,
            ),
        )
        query = dict(
            advanced__include=False,
            form=dict(
                fields=dict(
                    status=Field.choice(
                        display_name="Status",
                        choices=lambda **_: [
                            "---",
                            "Underloaded",
                            "Overloaded",
                        ],
                    ),
                    gender=Field.choice(
                        display_name="Gender",
                        choices=lambda params, **_: [""] + list(set(Staff.objects.values_list("gender", flat=True))),
                        after="academic_group",
                    ),
                    academic_group=Field.choice(
                        display_name="Group",
                        choices=lambda params, **_: [""] + list(AcademicGroup.objects.all()),
                    ),
                ),
                actions__reset=Action.button(
                    display_name="Clear Filter",
                    attrs__type="reset",
                ),
            ),
            filters=dict(
                status__value_to_q=lambda value_string_or_f, **_: StaffTable.filter_status_into_query(value_string_or_f),
            ),
            include=lambda user, **_: user.is_staff,
        )
        iommi_style = floating_fields_style

    @staticmethod
    def filter_status_into_query(value_string_or_f: str) -> Q:
        """
        Converts as the 'status' value from the dropdown into a DB query filter.

        :param value_string_or_f: Should be either "Overloaded", "Underloaded" or "---" or potentiqlly None.
        :return: The query.
        """
        if value_string_or_f == "Underloaded":
            return Q(load_balance__lt=0)
        elif value_string_or_f == "Overloaded":
            return Q(load_balance__gt=0)
        else:
            return Q()

    @staticmethod
    def annotate_rows(rows: QuerySet) -> QuerySet:
        """
        Adds the load balance to the table rows, derived from the load columns.
        :param rows: The query to annotate.
        :return: The annotated query, with a 'load_balance' column.
        """
        return rows.annotate(load_balance=F("load_assigned") - F("load_target"))
