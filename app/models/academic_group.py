from logging import getLogger

from django.db.models import CharField

from app.models.common import ModelCommon
from users.models import CustomUser

logger = getLogger(__name__)


class AcademicGroup(ModelCommon):
    """
    Academic group, e.g. Astro, Theory, QLM...

    Named AcademicGroup to avoid collision with base Django Group,
    which is more about user permissions.
    """
    icon = "users"
    url_root = "academic_group"

    code = CharField(max_length=1, unique=True, blank=False, primary_key=True)
    short_name = CharField(max_length=16, unique=True, blank=False, db_index=True)
    name = CharField(max_length=128, unique=True, blank=False)

    class Meta:
        ordering = ('name',)
        verbose_name = 'Group'
        verbose_name_plural = 'Groups'

    def __str__(self):
        return f"{self.short_name}"

    def get_instance_header(self, text: str|None = None, suffix: str|None = None) -> str:
        """
        Uses the full name for the header of one of these
        :param text: Text of the header, unused.
        :return: A rendered header string with the name of the instance.
        """
        return super().get_instance_header(text=self.name, suffix=suffix)

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
