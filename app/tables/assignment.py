from iommi import Table

from app.models import Assignment

class AssignmentTable(Table):
    """

    """
    class Meta:
        auto__model = Assignment
        columns = dict(
            is_provisional__attrs__class = {'text-right': False, 'text-center': True},
            is_first_time__attrs__class = {'text-right': False, 'text-center': True},
        )

