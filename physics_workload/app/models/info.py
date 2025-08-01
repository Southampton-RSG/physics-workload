from django.contrib.auth.models import AbstractUser
from django.db.models import CharField, TextField
from django.utils.html import mark_safe

from app.models.common import ModelCommon


class Info(ModelCommon):
    """
    Used for user-editable info text at the top of forms or categories.
    """

    icon = "circle-info"
    url_root = "info"

    name: CharField = CharField(max_length=120, unique=True)
    page: CharField = CharField(max_length=120, primary_key=True)
    text: TextField = TextField(
        null=True,
        verbose_name="Information",
        help_text=mark_safe("This field is interpreted as <a href='https://www.markdownguide.org/cheat-sheet/'>Markdown</a>, and can be formatted."),
    )

    def __str__(self):
        """
        :return: The URL route for the page.
        """
        return f"{self.name}"

    def get_absolute_url(self) -> str:
        """
        :return: The URL of the edit view for the info
        """
        return f"/{self.page}"

    def get_edit_url(self) -> str:
        """

        :return:
        """
        return f"/{self.url_root}/{self.page}/edit/"

    def has_access(self, user: AbstractUser) -> bool:
        """
        Only users assigned to a task can see the details
        :param user: The user
        :return: True if the user is assigned to this task
        """
        return super().has_access(user)
