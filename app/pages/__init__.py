from iommi.path import register_path_decoding

from app.auth import has_access_decoder
from app.models import AcademicGroup, Unit, LoadFunction, StandardLoad

from iommi import register_search_fields
from app.models.staff import Staff
from app.models.task import Task


register_path_decoding(
    standard_load=lambda string, **_: StandardLoad.available_objects.get(year=int(string))
)
