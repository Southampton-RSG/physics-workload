"""
Handles the views for the Standard Load
"""
from django.utils.html import format_html
from iommi import Form, Header, Page, Table, html

from app.forms.standard_load import StandardLoadForm, StandardLoadFormNewYear
from app.models.standard_load import StandardLoad
from app.pages.components import Equations
from app.pages.components.suffixes import SuffixCreate, SuffixEdit
from app.style import floating_fields_style, horizontal_fields_style


class StandardLoadEdit(Page):
    """
    Edit the standard load
    """
    header = Header(
        lambda standard_load, **_: standard_load.get_instance_header(),
        children__suffix=SuffixEdit(),
    )
    form = StandardLoadForm.edit(
        h_tag=None,
        instance=lambda standard_load, **_: standard_load,
        iommi_style=horizontal_fields_style,
        fields=dict(
            notes__iommi_style=floating_fields_style,
            year__include=False,
            target_load_per_fte_calc__include=False,
        ),
        editable=True
    )


class StandardLoadNewYear(Page):
    """
    Edit the standard load, to produce a new year
    """
    header = Header(
        lambda standard_load, **_: format_html(
            standard_load.get_instance_header(),
        ),
        children__suffix=SuffixCreate(
            text=" / New Year ",
        )
    )
    form = StandardLoadFormNewYear.create(
        instance=lambda standard_load, **_: standard_load,
    )


class StandardLoadDetail(Page):
    """
    Shows details of the standard load
    """
    header = Header(
        lambda standard_load, **_: standard_load.get_instance_header(),
    )

    assignment = html.p(
        children=dict(
            header=Header("Assignment Factors"),
            equation=Equations(
                template="app/standard_load/equation_assignment.html",
            ),
            form=Form(
                auto__model=StandardLoad,
                instance=lambda standard_load, **_: standard_load,
                auto__include=[
                    'load_lecture', 'load_lecture_first',
                    'load_coursework_set',  'load_coursework_credit', 'load_coursework_marked',
                    'load_exam_credit', 'load_exam_marked',
                ],
                iommi_style=horizontal_fields_style,
                editable=False,
                actions__submit=None,
            )
        )
    )
    target = html.p(
        children=dict(
            header=Header("Target Factors"),
            equation=Equations(
                template="app/standard_load/equation_target.html",
            ),
            form=Form(
                auto__model=StandardLoad,
                instance=lambda standard_load, **_: standard_load,
                auto__include=[
                    'load_fte_misc', 'target_load_per_fte', 'target_load_per_fte_calc'
                ],
                fields=dict(
                    target_load_per_fte=dict(
                        initial=lambda standard_load, **_: standard_load.target_load_per_fte,
                    ),
                    target_load_per_fte_calc=dict(
                        initial=lambda standard_load, **_: standard_load.target_load_per_fte_calc if standard_load.target_load_per_fte_calc else '',
                    )
                ),
                iommi_style=horizontal_fields_style,
                editable=False,
                actions__submit=None,
            )
        )
    )
    notes = Form(
        auto=dict(
            model=StandardLoad,
            include=[
                'notes'
            ],
        ),
        instance=lambda standard_load, **_: standard_load,
        iommi_style=floating_fields_style,
        editable=False,
    )


class StandardLoadList(Page):
    """

    """
    header = Header(
        lambda params, **_: StandardLoad.get_model_header(),
    )
    table = Table(
        h_tag=None,
        auto__model=StandardLoad,
        auto__include=['year', 'target_load_per_fte_calc'],
        rows=lambda params, **_: StandardLoad.objects.all(),
        columns=dict(
            year__cell__url=lambda row, **_: row.get_absolute_url(),
            target_load_per_fte_calc=dict(
                cell__value=lambda row, **_: int(row.target_load_per_fte_calc) if row.target_load_per_fte_calc else "N/A",
            )
        ),
    )

