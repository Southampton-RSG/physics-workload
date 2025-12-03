from logging import Logger, getLogger
from typing import Dict

from django.contrib.auth import get_user_model
from django.db.models import CharField, IntegerField, Sum
from rules import add_perm, is_staff, predicate

from app.models.common import ModelCommon
from users.models import CustomUser

logger: Logger = getLogger(__name__)

User = get_user_model()


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
        verbose_name="Load balance",
        help_text="Final load balance for the current year. Positive if overloaded.",
    )
    load_balance_historic = IntegerField(
        default=0,
        verbose_name="Historic load balance",
        help_text="Total of previous end-of-year load balances. Positive if overloaded.",
    )

    class Meta:
        ordering = ("name",)
        verbose_name = "Group"
        verbose_name_plural = "Groups"

    def __str__(self):
        return f"{self.short_name}"

    def get_absolute_url(self) -> str:
        return f"/{self.url_root}/{self.pk}/"

    def get_absolute_url_if_permitted(self, user) -> str|None:
        if user.has_perm("app.view_academicgroup", self):
            return self.get_absolute_url()
        else:
            return None

    def get_short_name(self) -> str:
        """
        :return: The short name. Needed for parity with the Unit model, for Task ownership.
        """
        return self.short_name

    def get_instance_header(self, text: str | None = None) -> str:
        """
        Uses the full name for the header of one of these.

        :param text: Text of the header, unused.
        :return: A rendered header string with the name of the instance.
        """
        return super().get_instance_header(text=self.name)

    def update_load(self) -> bool:
        """
        Updates the load balance for the group

        :return: True if the load has changed.
        """
        aggregates: Dict[str, int] = self.staff_set.aggregate(Sum("load_target"), Sum("load_assigned"))
        load_target: int = aggregates["load_target__sum"] if aggregates["load_target__sum"] else 0
        load_assigned: int = aggregates["load_assigned__sum"] if aggregates["load_assigned__sum"] else 0

        self.load_balance_final = load_assigned - load_target
        self.save()

    def get_load_balance(self) -> int:
        """
        Gets the load balance of all the group members.

        :return: The load balance.
        """
        aggregates: Dict[str, int] = self.staff_set.aggregate(Sum("load_assigned"), Sum("load_target"))
        load_assigned: int = aggregates["load_assigned__sum"] if aggregates["load_assigned__sum"] else 0
        load_target: int = aggregates["load_target__sum"] if aggregates["load_target__sum"] else 0
        return load_assigned - load_target


@predicate
def is_group_member(user: User, academic_group: AcademicGroup) -> bool:
    """
    Is this user a member of this group?
    :param user:
    :param academic_group:
    :return:
    """
    return academic_group.staff_set.contains(user.staff)


add_perm("app.add_academicgroup", is_staff)
add_perm("app.change_academicgroup", is_staff | is_group_member)
add_perm("app.delete_academicgroup", is_staff)
add_perm("app.view_academicgroup", is_staff | is_group_member)
