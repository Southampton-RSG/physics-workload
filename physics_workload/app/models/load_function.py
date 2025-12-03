from typing import Dict

from django.contrib.auth.models import AbstractUser, AnonymousUser
from django.core.validators import MinValueValidator
from django.db.models import CharField, CheckConstraint, F, IntegerField, Q, TextField
from django.utils.html import format_html
from rules import add_perm, always_true, is_staff
from simpleeval import simple_eval

from app.models.common import ModelCommon


class LoadFunction(ModelCommon):
    """
    Evaluatable Python expression that determines the load for a number of students,
    e.g. for number of tutees or when marking a dissertation.
    """

    icon = "calculator"
    url_root = "function"

    name = CharField(max_length=128, unique=True)
    expression = TextField(
        blank=False,
        verbose_name="Weighting Expression",
        help_text=format_html(
            "Where $s$ is the number of students. Evaluated using the <a class='font-monospace' href='https://github.com/danthedeckie/simpleeval'>simpleeval</a> Python module."
        ),
    )

    plot_minimum = IntegerField(
        null=True,
        blank=True,
        help_text="If provided, range to plot function over.",
        validators=[MinValueValidator(1)],
    )
    plot_maximum = IntegerField(
        null=True,
        blank=True,
        help_text="If provided, range to plot function over.",
        validators=[MinValueValidator(2)],
    )

    notes = TextField(blank=True)

    def __str__(self) -> str:
        return f"{self.name}"

    class Meta:
        ordering = ("name",)
        verbose_name = "Load Function"
        verbose_name_plural = "Load Functions"
        constraints = [
            CheckConstraint(
                check=(Q(plot_minimum__lt=F("plot_maximum")) & Q(plot_maximum__isnull=False))
                | (Q(plot_minimum__isnull=True) & Q(plot_maximum__isnull=True)),
                name="plot_range_valid",
                violation_error_message="Minimum range must be below maximum range if either are provided.",
            )
        ]

    def evaluate(self, students: int | None, unit: object | None = None) -> float | None:
        """
        Runs the equation for a given number of students.

        :param students: The number of students.
        :param unit: The unit.
        :return: The output of the equation.
        """
        names: Dict[str, int] = {}

        if students is not None:
            names["s"] = students

        if unit:
            names["l"] = unit.lectures
            names["e"] = unit.exams

        if len(names.keys()):
            return simple_eval(self.expression, names=names)
        else:
            return 0


add_perm("app.add_loadfunction", is_staff)
add_perm("app.change_loadfunction", is_staff)
add_perm("app.delete_loadfunction", is_staff)
add_perm("app.view_loadfunction", always_true)
