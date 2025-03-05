from iommi import Table

from app.models import Assignment

class AssignmentTable(Table):
    """

    """
    class Meta:
        auto__model = Assignment
        columns__is_provisional__attrs__class = {'text-right': False, 'text-center': True}
        columns__is_first_time__attrs__class = {'text-right': False, 'text-center': True}
