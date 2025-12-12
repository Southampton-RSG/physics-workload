from django.db.models import Case, Count, F, Q, QuerySet, When
from django.utils.safestring import mark_safe
from iommi import Column, Field, Table

from app.models import AcademicGroup, Assignment, LoadFunction, Task, Unit
from app.style import floating_fields_style


class TaskTable(Table):
    class Meta:
        auto = dict(
            model=Task,
            include=[
                "title",
                "load_calc",
                "load_calc_first",
                "assignment_set",
                "academic_group",
                "unit",
            ],
        )
        # ------- INVISIBLE COLUMNS --------
        columns__unit = Column(render_column=False)
        columns__academic_group = Column(render_column=False)
        columns__assignment_required = Column(render_column=False)
        columns__assignment_provisional = Column(render_column=False)
        # -------- VISIBLE COLUMNS --------
        columns__owner = Column(
            cell=dict(
                value=lambda row, **_: TaskTable.get_owner_for_task(row),
                url=lambda value, user, **_: value.get_absolute_url_if_permitted(user) if value else None,
            ),
            auto_rowspan=True,
            filter=dict(
                include=True,
                freetext=True,
            ),
            sortable=True,
        )
        columns__title = dict(
            after="owner",
            cell__url=lambda row, user, **_: row.get_absolute_url_if_permitted(user),
            filter=dict(
                include=True,
                freetext=True,
            ),
        )
        columns__load_calc = dict(
            after="title",
            display_name="Normal",
            group="Load",
            include=lambda user, **_: user.is_staff,
            cell=dict(
                value=lambda row, **_: row.load_calc
                if row.assignment_students != Task.AssignmentStudentsChoices.REQUIRED
                else mark_safe(f"<i class='fa fa-{LoadFunction.icon}'></i>"),
                url=lambda row, **_: None
                if row.assignment_students != Task.AssignmentStudentsChoices.REQUIRED
                else row.load_function.get_absolute_url(),
            ),
        )
        columns__load_calc_first = dict(
            after="load_calc",
            cell__value=lambda row, **_: row.load_calc_first if row.load_calc_first != row.load_calc else None,
            display_name="First time",
            group="Load",
            include=lambda user, **_: user.is_staff,
        )
        columns__assignment_set = dict(
            cell=dict(
                template="app/task/assignment_set.html",
                value=lambda row, **_: Assignment.objects.filter(task=row).all(),
            ),
            display_name="Assignment(s)",
            after="load_calc_first",
        )
        # -------- QUERY MODIFICATIONS --------
        query = dict(
            advanced__include=False,
            form=dict(
                fields__status=Field.choice(
                    display_name="Status",
                    choices=[
                        "---",
                        "Has Provisional",
                        "Missing Required",
                    ],
                ),
            ),
        )
        page_size = 50
        iommi_style = floating_fields_style
        empty_message = "No tasks available."

        @staticmethod
        def query__filters__status__value_to_q(value_string_or_f, **_) -> Q:
            if value_string_or_f == "Missing Required":
                return Q(assignment_required__gt=0)
            elif value_string_or_f == "Has Provisional":
                return Q(assignment_provisional__gt=0)
            else:
                return Q()

    @staticmethod
    def get_owner_for_task(task: Task) -> AcademicGroup | Unit | None:
        if task.academic_group:
            return task.academic_group
        elif task.unit:
            return task.unit
        else:
            return None

    @staticmethod
    def annotate_query_set(query_set: QuerySet[Task]) -> QuerySet[Task]:
        """
        Annotates the passed QuerySet with any additional data needed for columns,
        convenience method to keep consistent between uses.
        :param query_set: QuerySet to annotate.
        :return: Annotated QuerySet, with the number of assignments needed added as `assignment_open`
        """
        return query_set.annotate(
            assignment_required=Case(
                When(is_required=True, then=1),
                default=0,
            )
            - Count("assignment_set"),
            assignment_provisional=Count("assignment_set__is_provisional"),
            owner=Case(
                When(
                    academic_group__isnull=False,
                    then=F("academic_group__name"),
                ),
                When(
                    unit__isnull=False,
                    then=F("unit__code"),
                ),
                default=None,
            ),
        ).order_by("owner")
