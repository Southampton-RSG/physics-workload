from django.db.models import Count, Q, QuerySet
from iommi import Action, Column, Field, Table

from app.models import Task, Unit
from app.style import floating_fields_style


class UnitTable(Table):
    class Meta:
        auto = dict(model=Unit, include=["code", "name", "task_set", "students"])
        columns = dict(
            # -------- HIDDEN COLUMNS --------
            assignment_required=Column(render_column=False),
            assignment_provisional=Column(render_column=False),
            # -------- VISIBLE COLUMNS ------
            code=dict(
                cell__url=lambda row, request, **_: row.get_absolute_url_authenticated(request.user),
                filter=dict(
                    include=True,
                    freetext=True,
                ),
            ),
            name=dict(
                cell__url=lambda row, request, **_: row.get_absolute_url_authenticated(request.user),
                filter=dict(
                    include=True,
                    freetext=True,
                ),
            ),
            task_set=dict(
                display_name="Tasks",
                cell=dict(
                    template="app/unit/task_set.html",
                    value=lambda request, row, **_: Task.objects.filter(unit=row) if row.has_access(request.user) else None,
                ),
                after="students",
                sort_key="assignment_required",
                sortable=True,
            ),
        )
        # -------- FILTER --------
        query = dict(
            advanced__include=False,
            filters=dict(
                status=dict(
                    value_to_q=lambda value_string_or_f, **_: UnitTable.filter_status_into_query(value_string_or_f),
                )
            ),
            form=dict(
                fields__status=Field.choice(
                    include=lambda request, **_: request.user.is_staff,
                    display_name="Status",
                    choices=[
                        "---",
                        "Has Provisional",
                        "Has Unassigned",
                    ],
                ),
                actions__reset=Action.button(display_name="Clear Filter", attrs__type="reset"),
            ),
        )
        page_size = 20
        h_tag = None
        iommi_style = floating_fields_style

    @staticmethod
    def filter_status_into_query(value_string_or_f) -> Q:
        if value_string_or_f == "Has Unassigned":
            return Q(assignment_required__gt=0)
        elif value_string_or_f == "Has Provisional":
            return Q(assignment_provisional__gt=0)
        else:
            return Q()

    @staticmethod
    def annotate_query_set(query_set: QuerySet[Unit]) -> QuerySet[Unit]:
        return query_set.annotate(
            assignment_required=Count("task_set__is_required", filter=Q(task_set__is_required=True)) - Count("task_set__assignment_set"),
            assignment_provisional=Count("task_set__assignment_set__is_provisional"),
        )
