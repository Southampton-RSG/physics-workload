from typing import Dict, Type
from logging import getLogger

from django.contrib.auth.models import AbstractUser, AnonymousUser
from django.core.validators import MinValueValidator
from django.db.models import IntegerField, FloatField, TextField
from django.conf import settings
from django.db.models import ObjectDoesNotExist, Sum
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from app.models.common import ModelCommon
from app.models.staff import Staff
from app.models.assignment import Assignment
from app.models.task import Task


logger = getLogger(__name__)


class StandardLoad(ModelCommon):
    """
    Standard loads for an academic year
    """
    icon = 'weight-hanging'
    url_root = 'standard_load'

    year = IntegerField(
        unique=True,
        primary_key=True,
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
        help_text=r"$L_m$, basic allowance apart from explicit task loads"
    )
    target_load_per_fte = IntegerField(
        blank=False, null=False,
        validators=[
            MinValueValidator(0),
        ],
        verbose_name="Default teaching load per FTE",
        help_text="Used when calculating target load hours",
    )

    target_load_per_fte_calc = IntegerField(
        blank=True, null=True,
        verbose_name="Calculated teaching load per FTE",
    )

    notes = TextField(blank=True)

    class Meta:
        get_latest_by = 'year'
        ordering = ['-year']
        verbose_name='Standard Load'
        verbose_name_plural='Standard Loads'

    def __str__(self) -> str:
        return f"{self.year-2000}/{self.year-1999}"

    def get_absolute_url(self) -> str:
        """
        The standard load is always
        :return:
        """
        return f'/load/{self.year}/'

    def get_instance_header(self, text: str|None = None, suffix: str|None = None) -> str:
        """
        Prepend the instance name with 'Standard Load' for clarity
        :return: Header in the format "Standard Load ??/??"
        """
        return super().get_instance_header(text=f"Standard Load {self}")

    def has_access(self, user: AbstractUser|AnonymousUser) -> bool:
        """
        You can always see the load details
        :param user: The user to test access for.
        :return: True, always
        """
        return True

    def update_target_load_per_fte(self):
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

        target_old: int = self.target_load_per_fte_calc

        staff_aggregation: Dict[str, int] = Staff.objects.aggregate(Sum('fte_fraction'), Sum('hours_fixed'))
        total_fixed_hours: int = staff_aggregation.get('hours_fixed__sum', 0)
        total_fte_fraction: int = staff_aggregation.get('fte_fraction__sum', 0)
        assignment_aggregation: Dict[str, int] = Assignment.objects.aggregate(Sum('load_calc'))
        total_assigned_hours: int = assignment_aggregation.get('load_calc__sum', 0)

        if total_fte_fraction and total_assigned_hours:
            self.target_load_per_fte_calc = int(self.load_fte_misc + (total_assigned_hours - total_fixed_hours) / total_fte_fraction)
        else:
            self.target_load_per_fte_calc = int(self.target_load_per_fte)

        logger.info(f"Recalculated load target per FTE from {target_old} to {self.target_load_per_fte_calc}.")
        self.save()


    def update_calculated_loads(
            self,
            previous_standard_load: 'StandardLoad' = None,
    ) -> bool:
        """

        :param previous_standard_load: The previous version of the standard loads.
        :return: True if other models were updated, False otherwise.
        """
        logger.debug("Updating calculated loads...")

        if previous_standard_load:
            # Has an update actually changed the misc load? That would require a reevaluation of teaching workload.
            recalculate_target_load: bool = (self.load_fte_misc == previous_standard_load.load_fte_misc)
        else:
            # A staff member has been created/task has been deleted/whatever
            recalculate_target_load: bool = True

        for task in Task.objects.all():
            # Step over all tasks, and see if the changes to this form have changed the total load
            logger.debug(f"Updating task {task}...")
            if task.update_load():
                logger.debug(f"Updating task assignments...")

                for assignment in task.assignment_set.all():
                    logger.debug(f"Updating {assignment}...")
                    if assignment.update_load():
                        logger.debug(f"updating {assignment} staff...")
                        recalculate_target_load = True
                        assignment.staff.update_load_assigned()

        if not previous_standard_load or recalculate_target_load:
            logger.debug("Updating standard load year with new assigned total")
            self.update_target_load_per_fte()

            for staff in Staff.objects.all():
                staff.update_load_target()

        return recalculate_target_load
