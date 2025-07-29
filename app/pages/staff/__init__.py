"""
Handles the views for Staff
"""
from dash_bootstrap_templates import load_figure_template
from iommi import LAST, Field, Header, Page, html, register_search_fields

from app.forms.info import InfoForm
from app.forms.staff import StaffForm
from app.models import Info, Staff
from app.models.standard_load import StandardLoad
from app.pages.components.suffixes import SuffixCreate, SuffixDelete, SuffixEdit
from app.style import get_balance_classes_form
from app.tables.assignment import AssignmentStaffEditTable, AssignmentStaffTable
from app.tables.staff import StaffTable

load_figure_template('bootstrap_dark')

class StaffDelete(Page):
    """
    Page for deleting a Staff member.
    """
    header = Header(
        lambda staff, **_: staff.get_instance_header(),
        children__suffix=SuffixDelete(),
    )
    form = StaffForm.delete(
        h_tag=None,
        instance=lambda staff, **_: staff,
        auto__exclude=['user'],
        fields=dict(
            fte_fraction__include=lambda staff, **_: staff.fte_fraction,
            hours_fixed__include=lambda staff, **_: staff.hours_fixed,
            load_target__group='row2',
            load_assigned__group='row2',
            load_balance_historic__group='row2',
        )
    )


class StaffEdit(Page):
    """
    Page for editing the details of a Staff member
    """
    header = Header(
        lambda staff, **_: staff.get_instance_header(),
        children__suffix=SuffixEdit(),
    )
    form = StaffForm.edit(
        h_tag=None,
        auto__instance=lambda staff, **_: staff,
        auto__exclude=Staff.DYNAMIC_FIELDS + ['user'],
        fields=dict(
            load_external=dict(
                group='row25'
            ),
            load_balance=Field.integer(
                editable=False,
                group='row25',
                after='load_external',
                initial=lambda staff, **_: staff.get_load_balance(),
                non_editable_input__attrs__class=lambda field, **_: get_balance_classes_form(field.value),
                help_text="Load assigned minus target load. Positive if overloaded."
            ),
        )
    )


class StaffCreate(Page):
    """
    Create a new staff member
    """
    header = Header(
        lambda params, **_: Staff.get_model_header_singular(),
        children__suffix=SuffixCreate(),
    )
    form = StaffForm.create(
        h_tag=None,
        auto__exclude=Staff.DYNAMIC_FIELDS + ['user'],
        fields=dict(
            standard_load=Field.non_rendered(
                include=True,
                initial=lambda params, **_: StandardLoad.objects.latest(),
            )
        )
    )


class StaffDetail(Page):
    """
    Page showing the detail of a staff member, and setting their Assignments.
    """
    header = Header(
        lambda staff, **_: staff.get_instance_header()
    )
    text = html.p(
        "This staff member has not yet logged into this platform. "
        "Their staff account will be linked to their ActiveDirectory ID when they do.",
        include=lambda staff, **_: False if staff.user else True,
    )
    form = StaffForm(
        h_tag=None,
        auto=dict(
            instance=lambda staff, **_: staff,
            exclude=[
                'user', 'load_balance_final',
            ],
        ),
        fields=dict(
            fte_fraction__include=lambda staff, **_: staff.fte_fraction,
            hours_fixed__include=lambda staff, **_: staff.hours_fixed,
            load_target__group='row2',
            load_assigned__group='row2',
            load_external__group='row2',
            load_balance=Field.integer(
                group='row3',
                initial=lambda staff, **_: staff.get_load_balance(),
                non_editable_input__attrs__class=lambda field, **_: get_balance_classes_form(field.value),
                help_text="Load assigned minus target load. Positive if overloaded."
            ),
            load_balance_historic=dict(
                group = 'row3',
                after='load_balance',
                non_editable_input__attrs__class=lambda field, **_: get_balance_classes_form(field.value),
            ),
            notes=dict(
                include=lambda user, **_: user.is_staff,
                after=LAST,
                non_editable_input__attrs__class={
                    'form-control-plaintext': True,
                },
            ),
        ),
        editable=False,
        actions__submit=None,
    )
    assignments_editable = AssignmentStaffEditTable()
    assignments = AssignmentStaffTable()


class StaffList(Page):
    """
    List of all currently active staff.
    """
    header = Header(lambda params, **_: Staff.get_model_header())
    info = InfoForm(
        instance=lambda **_: Info.objects.get(page='staff'),
    )
    list = StaffTable(
        h_tag=None,
        rows=StaffTable.annotate_rows(
            Staff.objects
        ),
    )


register_search_fields(
     model=Staff,
    search_fields=[
        'name', 'gender', 'academic_group'
    ],
    allow_non_unique=True,
)
