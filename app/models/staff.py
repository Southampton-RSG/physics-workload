from datetime import datetime

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import Model, ForeignKey, TextField, BooleanField, CharField, FloatField, IntegerField, Manager
from django.db.models.deletion import PROTECT, SET_NULL

from app.models.academic_group import AcademicGroup
from app.models.managers import ActiveManager


class Staff(Model):
    """

    """
    user = ForeignKey(
        settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=SET_NULL,
    )
    account = CharField(
        max_length=16, unique=True, blank=False,
    )
    name = CharField(
        max_length=128, blank=False,
    )
    group = ForeignKey(
        AcademicGroup, blank=False, null=False, on_delete=PROTECT,
    )
    gender = CharField(
        max_length=1, blank=False,
    )
    type = CharField(
        max_length=16, blank=False,
    )
    notes = TextField(blank=True)

    is_active = BooleanField(default=True)
    objects_active = ActiveManager()
    objects = Manager()

    def __str__(self):
        return f"{self.name}"

    class Meta:
        ordering = ('is_active', 'name')
        verbose_name = 'Staff Member'
        verbose_name_plural = 'Staff Members'


class StaffYear(Model):
    """

    """
    staff = ForeignKey(
        Staff, blank=False, null=False, on_delete=PROTECT,
    )
    year = IntegerField(
        default=datetime.now().year,
        validators=[
            MinValueValidator(settings.YEAR_MINIMUM_VALUE),
            MaxValueValidator(datetime.now().year),
        ]
    )
    load_contract = FloatField()
    load_actual = FloatField()

    def __str__(self):
        return f"{self.staff} ({self.year})"

    class Meta:
        get_latest_by = 'year'
        ordering = ('year', 'staff')
        verbose_name = 'Workload Year'
        verbose_name_plural = 'Workload Years'


class StaffHours(Model):
    """

    """
    staff = ForeignKey(
        Staff, blank=False, null=False, on_delete=PROTECT
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
    is_updated = BooleanField(
        default=True, verbose_name="Updated for current year"
    )
    notes = TextField(blank=True)

    def __str__(self):
        return f"{self.staff} ({self.hours})"

    class Meta:
        ordering = ('is_updated', 'staff')
        verbose_name = 'Staff Hours'
        verbose_name_plural = 'Staff Hours'
