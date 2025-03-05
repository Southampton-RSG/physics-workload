from django.core.validators import MinValueValidator
from django.db.models import Model, CharField, TextField, BooleanField, Manager, IntegerField, CheckConstraint, Q, F
from django.utils.html import format_html

from app.models.managers import ActiveManager
from app.models.mixins import ModelCommonMixin

from simpleeval import simple_eval


class LoadFunction(ModelCommonMixin, Model):
    """
    Evaluatable Python expression that determines the load for a number of students,
    e.g. for number of tutees or when marking a dissertation.
    """
    icon = 'calculator'
    url_root = 'load_function'

    name = CharField(
        max_length=128, unique=True
    )
    expression = TextField(
        blank=False, verbose_name="Weighting Expression",
        help_text=format_html(
            "Evaluated using the <a class='font-monospace' href='https://github.com/danthedeckie/simpleeval'>simpleeval</a> Python module."
        )
    )
    is_active = BooleanField(default=True)
    objects_active = ActiveManager()
    objects = Manager()

    plot_minimum = IntegerField(
        null=True, blank=True, help_text="If provided, range to plot function over.",
        validators=[MinValueValidator(1)],
    )
    plot_maximum = IntegerField(
        null=True, blank=True, help_text="If provided, range to plot function over.",
        validators=[MinValueValidator(2)],
    )

    notes = TextField(blank=True)

    def __str__(self) -> str:
        return f"{self.name}"

    class Meta:
        ordering = ('name',)
        verbose_name = 'Load Function'
        verbose_name_plural = 'Load Functions'
        constraints = [
            CheckConstraint(
                check=(
                    Q(plot_minimum__lt=F('plot_maximum')) & Q(plot_maximum__isnull=False)) | \
                    (Q(plot_minimum__isnull=True) & Q(plot_maximum__isnull=True)
                 ),
                name='plot_range_valid',
                violation_error_message="Minimum range must be below maximum range if either are provided."
            )
        ]

    def evaluate(self, students: int) -> float:
        """
        Runs the equation for a given number of students.

        :param students: The number of students
        :return: The output of the equation.
        """
        return simple_eval(self.expression, names={'s': students})
