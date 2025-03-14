from typing import Dict

from django.contrib.auth.models import AbstractUser, AnonymousUser
from django.core.validators import MinValueValidator
from django.db.models import Model, IntegerField, FloatField, TextField
from django.conf import settings
from django.db.models import ObjectDoesNotExist, Sum

from app.models.mixins import ModelCommonMixin
from app.models.staff import Staff
from app.models.assignment import Assignment


class StandardLoad(ModelCommonMixin, Model):
    """
    Standard loads for an academic year
    """
    icon = 'weight-hanging'
    url_root = 'standard_load'

    year = IntegerField(
        unique=True, primary_key=True,
        validators=[
            MinValueValidator(settings.YEAR_MINIMUM_VALUE),
        ],
        help_text="Initial year, e.g. 2000 for 2000-2001 academic year."
    )

    load_lecture = FloatField(
        blank=False, null=False,
        validators=[
            MinValueValidator(0.0),
        ],
        verbose_name="Load hours per lecture & problems class",
        help_text=r"$L_{lec}$",
    )
    load_lecture_first = FloatField(
        blank=False, null=False,
        validators=[
            MinValueValidator(0.0),
        ],
        verbose_name="Load hours per lecture & problems class for first-time assignment",
        help_text=r"$L_{lec}$ applied when co-ordinating a unit for the first time.",
    )

    load_coursework_set = FloatField(
        blank=False, null=False,
        validators=[
            MinValueValidator(0.0),
        ],
        verbose_name="Load hours per item of coursework prepared",
        help_text=r"$L_{cw, \mathrm{prep}}$",
    )
    load_coursework_credit = FloatField(
        blank=False, null=False,
        validators=[
            MinValueValidator(0.0),
        ],
        verbose_name="Load hours per coursework CATS",
        help_text=r"$L_{cw, \mathrm{cats}}$",
    )
    load_coursework_marked = FloatField(
        blank=False, null=False,
        validators=[
            MinValueValidator(0.0),
        ],
        verbose_name="Load hours per (coursework plus coursework CATS) marked",
        help_text=r"$L_{cw, \mathrm{mark}}$",
    )

    load_exam_credit = FloatField(
        blank=False, null=False,
        validators=[
            MinValueValidator(0.0),
        ],
        verbose_name="Load hours per exam CATS",
        help_text=r"$L_{e, \mathrm{cats}}$",
    )
    load_exam_marked = FloatField(
        blank=False, null=False,
        validators=[
            MinValueValidator(0.0),
        ],
        verbose_name="Load hours per exam marked",
        help_text=r"$L_{e, \mathrm{mark}}$",
    )
    load_fte_misc = FloatField(
        blank=False, null=False,
        validators=[
            MinValueValidator(0.0),
        ],
        verbose_name="Staff misc. load per FTE fraction",
        help_text="Basic allowance apart from explicit task loads"
    )
    hours_fte = FloatField(
        blank=False, null=False,
        validators=[
            MinValueValidator(0.0),
        ],
        verbose_name="Backstop 'hours per FTE' value",
        help_text="Used when calculating target load hours",
    )

    hours_fte_calc = FloatField(
        blank=True, null=True,
        verbose_name="Calculated teaching hours per FTE",
        help_text="Used when calculating target load hours",
    )

    notes = TextField(blank=True)

    class Meta:
        get_latest_by = 'year'
        ordering = ['-year']
        verbose_name='Standard Load'
        verbose_name_plural='Standard Loads'

    def __str__(self) -> str:
        return f"Load {self.year-2000}/{self.year-1999}"

    def has_access(self, user: AbstractUser|AnonymousUser) -> bool:
        """You can always see the load details"""
        return True

    def calculate_teaching_hours(self):
        """

        :return:
        """
        # C = FTE fraction (raw) - staff.fte_fraction
        # D = Fixed hours (raw) - staff.hours_fixed
        # E = Equivalent FTE - either actual FTE [C], or fixed hours [D] / 'average teaching per staff' [J61]
        # F = Sum of workload for each staff member (sum of staff.assignment_set.load_calc)
        # G = Duplicate of [F], for a subset. Deprecated?
        # H = For FTE staff, standard_load.misc_load * FTE fraction [C]
        # I = Total load (including misc fraction [H] and all assignments [F])
        # J = What the calculated 'average' load is, scaled to that employee's FTE Fraction [E]
        # J58 = The sum of all workloads for FTE=1.0 staff, divided by the number of FTE=1.0 staff
        # J60 = The 'average' of 'average load scaled per FTE' (old algorithm)
        # J61 = The sum of all workloads inc. misc [I] / the sum of all FTE fractions [E]
        # H_{teaching} = \frac{\sum H_{assigned} + \sum F_{contract} * H_{misc}}{\sum F_{contract} + \frac{\sum H_{fixed}}{H_{teaching}}}
        # H_{teaching} \sum F_{contract} + \sum H_{fixed} = \sum H_{assigned} + \sum F_{contract} * H_{misc}
        # H_{teaching} = \frac{\sum H_{assigned} + \sum F_{contract} * H_{misc} - \sum H_{fixed}}{\sum F_{contract}}

        staff_aggregation: Dict[str, float] = Staff.objects_active.aggregate(Sum('fte_fraction'), Sum('hours_fixed'))
        total_fixed_hours: float = staff_aggregation['hours_fixed']
        total_fte_fraction: float = staff_aggregation['fte_fraction']
        total_assigned_hours: float = Assignment.objects.filter(year=self.year).aggregate(Sum('load_calc'))['load_calc']

        self.hours_fte_calc = self.load_fte_misc + (total_assigned_hours-total_fixed_hours) / total_fte_fraction
        self.save()

def get_current_standard_load() -> StandardLoad|None:
    """
    Wrapper to get current load in a way that won't crash during DB initialisation when it doesn't exit yet.
    :return: Gets the current standard load, or None if it's not yet initialised.
    """
    try:
        return StandardLoad.objects.latest()
    except ObjectDoesNotExist:
        return None
