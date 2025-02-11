from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Model, ForeignKey, PROTECT, FloatField, IntegerField, TextField
from django.urls import reverse_lazy

from app.models.staff import Staff
from app.models.academic_year import AcademicYear


class StaffYear(Model):
    """

    """
    staff = ForeignKey(
        Staff, blank=False, null=False, on_delete=PROTECT,
    )
    academic_year = ForeignKey(
        AcademicYear, blank=False, null=False, on_delete=PROTECT,
    )
    load_contract = FloatField(
        blank=True, null=True, validators=[MinValueValidator(0.0)],
        help_text="Contracted load hours",
    )
    load_actual = FloatField(
        blank=True, null=True, validators=[MinValueValidator(0.0)],
        help_text="Worked load hours",
    )

    hours = IntegerField(
        blank=True, null=True, verbose_name="Fixed hours",
        validators=[
            MinValueValidator(0),
            MaxValueValidator(settings.HOURS_MAXIMUM_VALUE),
        ],
    )
    fte_fraction = FloatField(
        blank=True, null=True, verbose_name="FTE fraction",
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1),
        ],
    )
    notes = TextField(blank=True)

    class Meta:
        get_latest_by = 'academic_year'
        unique_together = ('staff', 'academic_year')
        ordering = ('academic_year', 'staff')
        verbose_name = 'Workload Year'
        verbose_name_plural = 'Workload Years'

    def __str__(self):
        return f"{self.staff} ({self.academic_year})"

    @property
    def load(self) -> float:
        """
        :return: Returns the load if it has been calculated, calculates and caches it if not.
        """
        if not self.load_actual:
            self.load_actual = self.calculate_load()

        return self.load_actual

    def calculate_load(self) -> float:
        """
        :return: The total of all the assignments set for this staff member this year.
        """
        return sum(self.assignment_set.values_list('load', flat=True))

    def get_absolute_url(self) -> str:
        return reverse_lazy('staff_year_detail', args=[self.pk])