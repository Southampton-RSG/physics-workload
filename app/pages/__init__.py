from iommi.path import register_path_decoding

from app.auth import has_access_decoder
from app.models import AcademicGroup, Unit, LoadFunction, StandardLoad

from iommi import register_search_fields
from app.models.staff import Staff
from app.models.task import Task


register_search_fields(
     model=Staff, search_fields=['name', 'gender', 'academic_group'], allow_non_unique=True,
)
register_search_fields(
    model=Task, search_fields=['name'], allow_non_unique=True
)

register_path_decoding(
    unit=has_access_decoder(Unit, "You must be assigned to a Unit to view it"),
)
register_path_decoding(
    academic_group=has_access_decoder(AcademicGroup, "You must be a member of this Group to view it."),
)
register_path_decoding(
    task=has_access_decoder(Task, "You must be assigned to a Task to view it."),
)
register_path_decoding(
    staff=has_access_decoder(Staff, "You may only view your own Staff details."),
)
register_path_decoding(
    staff_history=lambda string, **_: Staff.history.get(history_id=int(string)),
)
register_path_decoding(
    load_function=lambda string, **_: LoadFunction.available_objects.get(pk=int(string))
)
register_path_decoding(
    standard_load=lambda string, **_: StandardLoad.available_objects.get(year=int(string))
)
