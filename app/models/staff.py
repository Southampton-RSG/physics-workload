from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Model, ForeignKey, TextField, BooleanField, CharField, Manager, FloatField, IntegerField, Index
from django.db.models.deletion import PROTECT, SET_NULL
from django.urls import reverse_lazy
from model_utils.managers import QueryManager

from app.models.academic_group import AcademicGroup



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
    academic_group = ForeignKey(
        AcademicGroup, blank=False, null=False, on_delete=PROTECT,
        verbose_name='Group',
    )
    gender = CharField(
        max_length=1, blank=False,
        help_text="Single-letter code"
    )
    type = CharField(
        max_length=16, blank=False,
    )
    notes = TextField(blank=True)

    load_calculated_target = FloatField(
        blank=True, null=True, validators=[MinValueValidator(0.0)],
        help_text="Target load hours",
    )
    load_calculated_worked = FloatField(
        blank=True, null=True, validators=[MinValueValidator(0.0)],
        help_text="Worked load hours",
    )
    load_balance = FloatField(
        default=0,
        help_text="Ongoing load balance",
    )

    hours_fixed = IntegerField(
        blank=True, null=True, verbose_name="Fixed hours (non-FTE)",
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

    is_active = BooleanField(default=True)
    objects_active = QueryManager(is_active=True)
    objects = Manager()

    class Meta:
        ordering = ('is_active', 'name')
        verbose_name = 'Staff Member'
        verbose_name_plural = 'Staff Members'
        indexes = [
            Index(fields=['name']),
            Index(fields=['gender']),
            Index(fields=['academic_group']),
        ]

    def __str__(self):
        return f"{self.name}"

    def get_absolute_url(self) -> str:
        return reverse_lazy('staff_detail', args=[self.account])
