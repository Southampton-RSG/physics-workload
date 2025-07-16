from logging import getLogger, Logger
from typing import Dict

from django.db.models import CharField, IntegerField, Sum

from app.models.common import ModelCommon
from users.models import CustomUser


logger: Logger = getLogger(__name__)


class AcademicGroup(ModelCommon):
    """
    Academic group, e.g. Astro, Theory, QLM...

    Named AcademicGroup to avoid collision with base Django Group,
    which is more about user permissions.
    """
    icon = "users"
    url_root = "group"

    code = CharField(max_length=1, unique=True, blank=False, primary_key=True)
    short_name = CharField(max_length=16, unique=True, blank=False, db_index=True)
    name = CharField(max_length=128, unique=True, blank=False)

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

    class Meta:
        ordering = ('name',)
        verbose_name = 'Group'
        verbose_name_plural = 'Groups'

    def __str__(self):
        return f"{self.short_name}"

    def get_short_name(self) -> str:
        """
        :return: The short name. Needed for parity with the Unit model, for Task ownership.
        """
        return self.short_name

    def get_instance_header(self, text: str|None = None) -> str:
        """
        Uses the full name for the header of one of these.

        :param text: Text of the header, unused.
        :return: A rendered header string with the name of the instance.
        """
        return super().get_instance_header(text=self.name)

    def has_access(self, user: CustomUser) -> bool:
        """
        Only users assigned who are members of an academic group can view it.

        :param user: The user.
        :return: True if the user is allowed to view the group.
        """
        if super().has_access(user):
            return True

        elif not user.is_anonymous:
            return user.staff.academic_group == self

        return False

    def update_load(self) -> bool:
        """
        Updates the load balance for the group

        :return: True if the load has changed.
        """
        aggregates: Dict[str, int] = self.staff_set.aggregate(
            Sum('load_target'), Sum('load_assigned')
        )
        load_target: int = aggregates['load_target__sum'] if aggregates['load_target__sum'] else 0
        load_assigned: int = aggregates['load_assigned__sum'] if aggregates['load_assigned__sum'] else 0

        self.load_balance_final = load_assigned - load_target
        self.save()

    def get_load_balance(self) -> int:
        """
        Gets the load balance of all the group members.

        :return: The load balance.
        """
        aggregates: Dict[str, int] = self.staff_set.aggregate(Sum('load_assigned'), Sum('load_target'))
        load_assigned: int = aggregates['load_assigned__sum'] if aggregates['load_assigned__sum'] else 0
        load_target: int = aggregates['load_target__sum'] if aggregates['load_target__sum'] else 0
        return load_assigned - load_target
