from typing import Dict, Type
from logging import getLogger
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import (
    Model, ForeignKey, TextField, BooleanField, CharField, Manager, FloatField, IntegerField, Index, CheckConstraint, Q, Sum
)
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver
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

    load_target = FloatField(
        default=0, validators=[MinValueValidator(0.0)],
        verbose_name='Load target',
        help_text="Load hours calculated for the current year.",
    )
    load_assigned = FloatField(
        default=0, validators=[MinValueValidator(0.0)],
        verbose_name='Load assigned',
        help_text="Load hours assigned for the current year.",
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

    standard_load = ForeignKey(
        'StandardLoad', on_delete=PROTECT,
        verbose_name="Year",
    )

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
                check=
                    (Q(fte_fraction__gt=0) & Q(hours_fixed__isnull=True)) |
                    (Q(fte_fraction__isnull=True) & Q(hours_fixed__gt=0))
                ,
                name='fixed_or_fte',
                violation_error_message="Staff must be fixed or FTE; please leave one field blank."
            )
        ]

    def __str__(self):
        """
        Default rendering of a staff member shows their load balance
        :return: Their name plus load balance.
        """
        return f"{self.name} [{self.load_assigned - self.load_target:.0f}]"

    def get_instance_header(self) -> str:
        """
        Creates a header for staff, without their load balance in.
        :return: A header with just the name
        """
        return super().get_instance_header(text=self.name)

    def get_load_balance(self):
        """
        :return: The load balance
        """
        return self.load_assigned - self.load_target

    def update_load_assigned(self):
        """
        Updates own assigned load by summing the load of the assignments.
        :return: True if the total load has changed, false if not.
        """
        load_assigned = self.assignment_set.aggregate(Sum('load_calc'))['load_calc__sum']
        if self.load_assigned !=- load_assigned:
            self.load_assigned = load_assigned
            return True

        else:
            return False


    def update_load_target(self):
        """
        Updates the target load from the standard load settings.
        :return: True if the load target has changed, false if not.
        """
        if self.hours_fixed:
            load_target = self.hours_fixed
        else:
            load_target = self.fte_fraction * self.standard_load.target_load_per_fte

        if self.load_target != load_target:
            self.load_target = load_target
            return True
        else:
            return False