from logging import getLogger
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import (
    Model, ForeignKey, TextField, BooleanField, CharField, Manager, FloatField, IntegerField, Index, CheckConstraint, Q
)
from django.db.models.deletion import PROTECT, SET_NULL
from django.utils.html import format_html
from model_utils.managers import QueryManager

from app.models.academic_group import AcademicGroup
from app.models.mixins import ModelCommonMixin

logger = getLogger(__name__)


class Staff(ModelCommonMixin, Model):
    """
    Member of staff; not necessarily a current user.
    """
    icon = 'user'
    url_root = 'staff'

    user = ForeignKey(
        settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=SET_NULL,
    )
    account = CharField(
        max_length=16, unique=True, blank=False, primary_key=True,
        help_text=format_html("Active Directory account e.g. <tt>js1a25</tt>")
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
        verbose_name='Load target',
        help_text="Load hours calculated for the current year.",
    )
    load_calculated_assigned = FloatField(
        default=0, validators=[MinValueValidator(0.0)],
        verbose_name='Load assigned',
        help_text="Load hours assigned for the current year.",
    )
    load_calculated_balance = FloatField(
        default=0,
        verbose_name='Load balance',
        help_text="The current year's target load minus assigned load.",
    )

    hours_fixed = IntegerField(
        blank=True, null=True, verbose_name="Fixed teaching hours",
        help_text="Must be empty if staff are FTE fraction.",
        validators=[
            MinValueValidator(0),
            MaxValueValidator(settings.HOURS_MAXIMUM_VALUE),
        ],
    )
    fte_fraction = FloatField(
        blank=True, null=True, verbose_name="FTE fraction teaching",
        help_text="Must be empty if staff are fixed-hours.",
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
        constraints = [
            CheckConstraint(
                check=(
                    Q(fte_fraction__gt=0) & Q(fixed_hours__isnull=0) | \
                    (Q(fte_fraction__isnull=True) & Q(fixed_hours__gt=0))
                 ),
                name='fixed_or_fte',
                violation_error_message="Staff must be fixed or FTE; please leave one field blank."
            )
        ]

    def __str__(self):
        """
        Default rendering of a staff member shows their load balance
        :return: Their name plus load balance.
        """
        return f"{self.name} [{self.load_calculated_balance:.0f}]"

    def get_instance_header(self) -> str:
        """
        Creates a header for staff, without their load balance in.
        :return: A header with just the name
        """
        return super().get_instance_header(text=self.name)

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
