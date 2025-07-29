from logging import Logger, getLogger

from django.db.models import F, Q, QuerySet
from iommi import Action, Column, Field, Table

from app.auth import has_staff_access
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
                    url=lambda row, request, **_: row.get_absolute_url_authenticated(request.user),
                    value=lambda row, **_: row.account if not row.account.startswith("unconnected") else None,
                ),
            ),
            name=dict(
                cell__url=lambda row, request, **_: row.get_absolute_url_authenticated(request.user),
                filter=dict(
                    include=True,
                    freetext=True,
                ),
            ),
            academic_group=Column(
                after="name",
                display_name="Group",
                filter__include=True,
                cell__url=lambda row, request, **_: row.academic_group.get_absolute_url_authenticated(request.user) if row.academic_group else None,
            ),
            gender=dict(
                filter__include=True,
                render_column=False,
            ),
            assignment_set=dict(
                include=lambda user, **_: user.is_staff,
                cell__value=lambda row, **_: Assignment.objects.filter(staff=row),
                cell__template="app/staff/assignment_set.html",
            ),
            load_balance_historic=dict(
                group="Load Balance",
                display_name="Historic",
                cell=dict(
                    value=lambda request, row, **_: row.load_balance_historic if row.has_access(request.user) else None,
                    attrs__class=lambda row, **_: get_balance_classes(row.load_balance_historic),
                ),
                include=lambda request, **_: request.user.is_staff,
            ),
            load_balance=dict(
                group="Load Balance",
                display_name="Current",
                cell=dict(
                    value=lambda request, row, **_: row.load_balance if row.has_access(request.user) else None,
                    attrs__class=lambda row, **_: get_balance_classes(row.load_balance),
                ),
                include=lambda request, **_: request.user.is_staff,
            ),
        )
        query = dict(
            advanced__include=False,
            include=lambda request, **_: has_staff_access(request.user),
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
        )
        # empty_message="No staff available.
        iommi_style = floating_fields_style

    @staticmethod
    def filter_status_into_query(value_string_or_f: str) -> Q:
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
