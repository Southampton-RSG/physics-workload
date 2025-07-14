from iommi import Field, Form

from app.models import Assignment, Task


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
            is_first_time__group="Row",
            is_provisional__group="Row",
        )



