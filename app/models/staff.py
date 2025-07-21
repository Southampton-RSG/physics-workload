from logging import Logger, getLogger

from django.conf import settings
from django.contrib.auth.models import AbstractUser, AnonymousUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import (
    CharField,
    CheckConstraint,
    FloatField,
    Index,
    IntegerField,
    OneToOneField,
    Q,
    Sum,
    TextField,
)
from django.db.models.deletion import PROTECT, SET_NULL
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.html import format_html
from simple_history.models import HistoricForeignKey

from app.models.academic_group import AcademicGroup
from app.models.common import ModelCommon
from users.models import CustomUser

logger: Logger = getLogger(__name__)


class Staff(ModelCommon):
    """
    Member of staff; not necessarily a current user.

    :attribute icon: Icon to use in the front end.
    :attribute url_root: Root URL for the model.
    :attribute user: The user account corresponding to this staff member, may be none.
    :attribute account: The active directory account name for this staff member.
    :attribute name: The name of this staff member.
    """
    DYNAMIC_FIELDS = [
        'load_balance_historic',
        'load_balance_final',
        'load_target',
        'load_assigned'
    ]

    icon = 'user'
    url_root = 'staff'

    user = OneToOneField(
        CustomUser,
        blank=True, null=True, on_delete=SET_NULL,
    )
    account = CharField(
        max_length=16,
        unique=True, blank=False, primary_key=True,
        help_text=format_html("Active Directory account e.g. <tt>js1a25</tt>")
    )
    name = CharField(
        max_length=128, blank=False,
    )
    academic_group = HistoricForeignKey(
        AcademicGroup, on_delete=PROTECT,
        null=True, blank=True,
        verbose_name='Group',
    )
    gender = CharField(
        max_length=1, blank=False,
        help_text="Single-letter code"
    )

    load_target = IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='Load target',
        help_text="Load hours calculated for the current year.",
    )
    load_assigned = IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='Load assigned',
        help_text="Load hours assigned for the current year.",
    )
    load_external = IntegerField(
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

    load_balance_final = IntegerField(
        default=0,
        verbose_name='Load balance',
        help_text="Final load balance for the current year. Positive if overloaded.",
    )
    load_balance_historic = IntegerField(
        default=0,
        verbose_name='Historic load balance',
        help_text="Total of previous end-of-year load balances. Positive if overloaded.",
    )

    notes = TextField(blank=True)

    class Meta:
        ordering = [
            'name'
        ]
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
        Does the user have access to this object?

        :param user: The user in question.
        :return: True if the user has access, or the user is this staff member.
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
        return f"{self.name} [{self.load_assigned - self.load_target}]"

    def get_instance_header(self, text:str|None = None) -> str:
        """
        Creates a header for staff, without their load balance in.

        :param text: Ignored, only exists to match signature.
        :return: A header with just the name.
        """
        return super().get_instance_header(text=self.name)

    def get_load_balance(self):
        """
        Gets how much under or overloaded the staff member is.

        :return: The balance of assigned load against target load, negative if underloaded.
        """
        return self.load_assigned - self.load_target

    def update_load_assigned(self):
        """
        Updates own assigned load by summing the load of the assignments.

        :return: True if the total load has changed, false if not.
        """
        from app.models.standard_load import StandardLoad

        load_assigned: int = StandardLoad.objects.latest().load_fte_misc * self.fte_fraction
        if assignment_total := self.assignment_set.aggregate(Sum('load_calc'))['load_calc__sum']:
            load_assigned += assignment_total

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
            load_target = self.fte_fraction * StandardLoad.objects.latest().target_load_per_fte_calc
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
    if '@' in instance.username:
        # If this isn't the default Django superuser (who won't have an email-based account)
        account: str = instance.username.split('@')[0]

        try:
            logger.info(f"Looking up a staff member for user '{instance.username}'")
            staff: Staff|None = Staff.objects.get(account=account)

        except Staff.DoesNotExist:
            # There's no staff member with this account name, so let's try surname...
            try:
                logger.info(f"No account match for {account}, looking for last name '{instance.last_name}'")
                staff = Staff.objects.get(name=instance.last_name)

            except Staff.DoesNotExist:
                logger.info(f"No staff with last name '{instance.last_name}'")
                staff = None

        # Don't create a staff record for the manual Django superuser
        # Otherwise, either create a new Staff model from their ActiveDirectory account,
        # or just update their Staff model with their full name from the AD account.

        staff, staff_created = Staff.objects.update_or_create(
            account=instance.username.split('@')[0],
            user=instance,
            defaults={
                'name': f"{instance.first_name} {instance.last_name}",
            }
        )
        if staff_created:
            logger.info(f"Created Staff: '{instance.username}' - {staff}")
        else:
            logger.info(f"Updated Staff: '{instance.username}' - {staff}")
