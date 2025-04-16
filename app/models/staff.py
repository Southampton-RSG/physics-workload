from typing import Dict, Type
from logging import getLogger
from django.conf import settings
from django.contrib.auth.models import AbstractUser, AnonymousUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import (
    Model, ForeignKey, TextField, BooleanField, CharField, Manager, FloatField, IntegerField, Index, CheckConstraint, Q, Sum
)
from django.db.models.deletion import PROTECT, SET_NULL
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.html import format_html

from simple_history.models import HistoricForeignKey

from users.models import CustomUser
from app.models.academic_group import AcademicGroup
from app.models.common import ModelCommon


logger = getLogger(__name__)


class Staff(ModelCommon):
    """
    Member of staff; not necessarily a current user.
    """
    icon = 'user'
    url_root = 'staff'

    user = HistoricForeignKey(
        CustomUser, blank=True, null=True, on_delete=SET_NULL,
    )
    account = CharField(
        max_length=16, unique=True, blank=False, primary_key=True,
        help_text=format_html("Active Directory account e.g. <tt>js1a25</tt>")
    )
    name = CharField(
        max_length=128, blank=False,
    )
    academic_group = ForeignKey(
        AcademicGroup, on_delete=PROTECT,
        null=True, blank=True,
        verbose_name='Group',
    )
    gender = CharField(
        max_length=1, blank=False,
        help_text="Single-letter code"
    )
    type = CharField(
        max_length=16, blank=True,
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
    load_external = FloatField(
        default=0,
        verbose_name="External load",
        help_text='Teaching load accrued externally to this tool this year.',
    )
    hours_fixed = IntegerField(
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(settings.HOURS_MAXIMUM_VALUE),
        ],
        verbose_name="Fixed teaching hours",
        help_text="Must be empty if staff are FTE fraction.",
    )
    fte_fraction = FloatField(
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1),
        ],
        verbose_name="FTE fraction teaching",
        help_text="Must be 0 if staff are fixed-hours.",
    )

    load_balance_final = FloatField(
        default=0,
        verbose_name='Load balance',
        help_text="Final load balance for the current year. Positive if overloaded.",
    )
    load_balance_historic = FloatField(
        default=0,
        verbose_name='Historic load balance',
        help_text="Total of previous end-of-year load balances. Positive if overloaded.",
    )

    notes = TextField(blank=True)

    # --------------------------------------------------------------------------
    # This block allow custom historical dating, used when importing data.
    # --------------------------------------------------------------------------
    __history_date = None

    @property
    def _history_date(self):
        return self.__history_date

    @_history_date.setter
    def _history_date(self, value):
        self.__history_date = value
    # --------------------------------------------------------------------------

    class Meta:
        ordering = ('is_removed', 'name')
        verbose_name = 'Staff Member'
        verbose_name_plural = 'Staff Members'
        indexes = [
            Index(fields=['name']),
            Index(fields=['gender']),
            Index(fields=['academic_group']),
        ]
        constraints = [
            CheckConstraint(
                check=(Q(fte_fraction=0) | Q(hours_fixed=0)),
                name='fixed_or_fte',
                violation_error_message="Staff must be fixed or FTE; please leave one field zero."
            )
        ]

    def has_access(self, user: AbstractUser|AnonymousUser) -> bool:
        """
        :param user:
        :return:
        """
        if super().has_access(user):
            return True
        else:
            return user == self.user

    def __str__(self):
        """
        Default rendering of a staff member shows their load balance
        :return: Their name plus load balance.
        """
        return f"{self.name} [{self.load_assigned - self.load_target:.0f}]"

    def get_instance_header(self, text:str|None = None, suffix: str|None = None) -> str:
        """
        Creates a header for staff, without their load balance in.
        :return: A header with just the name
        """
        return super().get_instance_header(text=self.name, suffix=suffix)

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
        from app.models.standard_load import StandardLoad

        load_assigned = self.assignment_set.aggregate(Sum('load_calc'))['load_calc__sum']
        load_assigned += StandardLoad.objects.latest().load_fte_misc * self.fte_fraction

        if self.load_assigned !=- load_assigned:
            self.load_assigned = load_assigned
            self.save()
            return True

        else:
            return False

    def update_load_target(self):
        """
        Updates the target load from the standard load settings.
        :return: True if the load target has changed, false if not.
        """
        from app.models import StandardLoad

        if self.hours_fixed:
            load_target = self.hours_fixed
        elif self.fte_fraction:
            load_target = self.fte_fraction * StandardLoad.available_objects.latest().target_load_per_fte_calc
        else:
            # This is someone who doesn't have set teaching hours, ignore
            return False

        if self.load_target != load_target:
            self.load_target = load_target
            self.save()
            return True
        else:
            return False


@receiver(post_save, sender=CustomUser)
def update_staff_link(sender, instance, created, **kwargs):
    """
    Link newly created CustomUser to a staff member.
    :param sender:
    :param instance:
    :param created:
    :param kwargs:
    :return:
    """
    logger.info(f"Inside User post_save for {instance}")
    # django_auth_adfs will first create, Django user with just the username (email), then
    # on a second call, update with first name, lastname, email etc.

    try:
        logger.info(f"Looking up a staff member for user {instance.username}")
        staff: Staff|None = Staff.objects.get(account=instance.username.split('@')[0])

    except Staff.DoesNotExist:
        # There's no staff member with this account name, so let's try surname...
        try:
            logger.info(f"No account match for {instance.username}, looking for last name")
            staff = Staff.objects.get(name=instance.last_name)

        except Staff.DoesNotExist:
            staff = None

    if staff:
        # If we found a staff member using either of those two methods...
        if not staff.user:
            # If they're not linked to the current user, then link them
            logger.info(f"Found existing staff member who is unlinked - linking.")
            staff.user = instance
            staff.save()

        elif staff.user != instance:
            # If they're linked, but not to the current user, then relink them
            logger.info(f"Found incorrectly linked staff member - relinking.")
            staff.user = instance
            staff.save()

        else:
            # If they're linked, and to the current user, then we don't have to do anything.
            logger.info(f"Found existing linked staff member.")

    if not instance.is_superuser:
        # Don't create a staff record for the manual Django superuser
        # Otherwise, either create a new Staff model from their ActiveDirectory account,
        # or just update their Staff model with their full name from the AD account.

        staff, staff_created = Staff.objects.update_or_create(
            account=instance.username.split('@')[0],
            defaults={
                'name': f"{instance.first_name} {instance.last_name}",
            }
        )
        if staff_created:
            logger.info(f"Created Staff: {instance.username} - {staff}")
        else:
            logger.info(f"Updated Staff: {instance.username} - {staff}")
