from logging import getLogger, DEBUG
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Model, ForeignKey, TextField, BooleanField, CharField, Manager, FloatField, IntegerField, Index, Sum
from django.db.models.deletion import PROTECT, SET_NULL
from model_utils.managers import QueryManager

from app.models.academic_group import AcademicGroup
from app.models.mixins import ModelIconMixin

logger = getLogger(__name__)


class Staff(ModelIconMixin, Model):
    """
    Member of staff; not necessarily a current user.
    """
    icon = 'user'
    url_root = 'staff'

    user = ForeignKey(
        settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=SET_NULL,
    )
    account = CharField(
        max_length=16, unique=True, blank=False, primary_key=True
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
        max_length=16, blank=True,
    )
    load_historic_balance = FloatField(
        default=0,
        verbose_name='Historic load balance',
        help_text="Sum of the load balance from previous years.",
    )

    load_calculated_target = FloatField(
        default=0, validators=[MinValueValidator(0.0)],
        verbose_name='Target load hours',
        help_text="Load hours calculated for the current year.",
    )
    load_calculated_assigned = FloatField(
        default=0, validators=[MinValueValidator(0.0)],
        verbose_name='Assigned load hours',
        help_text="Load hours assigned for the current year.",
    )
    load_calculated_balance = FloatField(
        default=0,
        verbose_name='Current load balance',
        help_text="The current year's target load minus assigned load.",
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

    notes = TextField(blank=True)

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

    def calculate_load_balance(self):
        """
        :return: The load balance for this staff member.
        """
        logger.debug(f"{self}: Updating load balance")

        load: float = 0
        for assignment in self.assignment_set.all():
            logger.debug(f"{self}: Adding load for {assignment}: {assignment.get_load()}")
            load += assignment.get_load()

        self.load_calculated_assigned = load
        self.load_calculated_balance = self.load_calculated_target - self.load_calculated_assigned
        self.save()
