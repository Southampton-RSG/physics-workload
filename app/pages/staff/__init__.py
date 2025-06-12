"""
Handles the views for Staff
"""
from iommi import Page, Field, Header, register_search_fields, LAST

from dash_bootstrap_templates import load_figure_template
load_figure_template('bootstrap_dark')

from app.models import Staff
from app.models.standard_load import StandardLoad
from app.forms.staff import StaffForm
from app.style import get_balance_classes
from app.tables.staff import StaffTable
from app.tables.assignment import AssignmentStaffTable
from app.pages.components.suffixes import SuffixCreate, SuffixEdit, SuffixDelete


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
        auto__exclude=['is_removed', 'user'],
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
        auto__exclude=Staff.DYNAMIC_FIELDS + ['is_removed', 'user'],
        fields=dict(
            load_external=dict(
                group='row25'
            ),
            load_balance=Field.integer(
                editable=False,
                group='row25',
                after='load_external',
                initial=lambda staff, **_: staff.get_load_balance(),
                non_editable_input__attrs__class=lambda staff, **_: {
                    'form-control-plaintext': True
                } | get_balance_classes(staff.get_load_balance()),
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
        auto__exclude=Staff.DYNAMIC_FIELDS + ['is_removed', 'user'],
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
    form = StaffForm(
        h_tag=None,
        auto=dict(
            instance=lambda staff, **_: staff,
            exclude=[
                'user', 'is_removed', 'load_balance_final',
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
                non_editable_input__attrs__class=lambda staff, **_: {
                    'form-control-plaintext': True
                } | get_balance_classes(staff.get_load_balance()),
                help_text="Load assigned minus target load. Positive if overloaded."
            ),
            load_balance_historic=dict(
                group = 'row3',
                after='load_balance',
                non_editable_input__attrs__class=lambda staff, **_: {
                    'form-control-plaintext': True,
                } | get_balance_classes(staff.get_load_balance()),
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
    assignments = AssignmentStaffTable()


class StaffList(Page):
    """
    List of all currently active staff.
    """
    header = Header(lambda params, **_: Staff.get_model_header())
    list = StaffTable(
        h_tag=None,
        rows=StaffTable.annotate_rows(
            Staff.available_objects
        ),
    )


register_search_fields(
     model=Staff,
    search_fields=[
        'name', 'gender', 'academic_group'
    ],
    allow_non_unique=True,
)
