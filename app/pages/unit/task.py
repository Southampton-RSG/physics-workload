from iommi import Header, Page

from app.forms.task import UnitTaskCreateForm, UnitTaskLeadCreateForm
from app.pages.components.suffixes import SuffixCreate, SuffixCreateTaskLead


class UnitTaskLeadCreate(Page):
    """
    Create a new unit lead
    """
    header = Header(
        lambda params, **_: params.unit.get_instance_header_short(),
        children__suffix=SuffixCreateTaskLead(),
    )
    form = UnitTaskLeadCreateForm.create()


class UnitTaskCreate(Page):
    """
    Create a task associated with a unit
    """
    header = Header(
        lambda params, **_: params.unit.get_instance_header_short(),
        children__suffix=SuffixCreate(),
    )
    form = UnitTaskCreateForm.create()
