from logging import Logger, getLogger

from iommi import Field, Form, Header

from app.models import Assignment, Task, Staff, StandardLoad
from app.utility import update_all_loads

logger: Logger = getLogger(__name__)


class AssignmentTaskUniqueForm(Form):
    """

    """
    class Meta:
        auto = dict(
            model=Assignment,
            include=[
                'task', 'staff', 'students', 'is_first_time', 'is_provisional',
            ]
        )
        title = "Assignment"
        fields = dict(
            task=Field.non_rendered(
                initial=lambda task, **_: task,
                editable=False,
                group="Row",
            ),
            students=dict(
                group="Row",
                include=lambda task, **_: not task.is_full_time and not task.is_lead,
            ),
            staff__group="Row",
            is_first_time__group="Row",
            is_provisional__group="Row",
        )
        extra__redirect_to='.'
        actions__submit=dict(
            display_name="Save",
            attrs__class={
                "btn-primary": False,
                "btn-success": True,
            }
        )

        @staticmethod
        def extra__on_delete(instance, **_):
            logger.info(f"Deleting assignment {instance}")
            update_all_loads()

        @staticmethod
        def extra__on_save(form, instance, **_):
            logger.info(f"Editing assignment {instance}, as {form.extra.crud_type}")
            update_all_loads()
