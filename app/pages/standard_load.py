"""
Handles the views for the Standard Load
"""
from django.urls import path

from iommi import Page, Table, html, Form, Column, Header, Action

from app.models.standard_load import StandardLoad
from app.forms.standard_load import StandardLoadForm
from app.pages.components import Equations
from app.pages.components.headers import HeaderInstanceEdit, HeaderInstanceDetail, HeaderList, HeaderInstanceHistory
from app.style import horizontal_fields_style, floating_fields_style



class StandardLoadEdit(Page):
    """
    Edit the standard load
    """
    header = HeaderInstanceEdit(
        lambda params, **_: params.standard_load.get_instance_header(),
    )
    form = StandardLoadForm.edit(
        h_tag=None,
        instance=lambda params, **_: params.standard_load,
        iommi_style=horizontal_fields_style,
        fields=dict(
            notes__iommi_style=floating_fields_style,
            year__include=False,
            is_removed=False,
        ),
        editable=True,
        extra__redirect_to='..',
    )


class StandardLoadDetail(Page):
    """
    Shows details of the standard load
    """
    header = HeaderInstanceDetail(
        lambda params, **_: params.standard_load.get_instance_header(),
    )

    assignment = html.p(
        children=dict(
            header=Header("Assignment Factors"),
            equation=Equations(
                template="app/standard_load/equation_assignment.html",
            ),
            form=Form(
                auto__model=StandardLoad, instance=lambda params, **_: params.standard_load,
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
                auto__model=StandardLoad, instance=lambda params, **_: params.standard_load,
                auto__include=[
                    'load_fte_misc', 'target_load_per_fte', 'target_load_per_fte_calc'
                ],
                fields=dict(
                    target_load_per_fte=dict(
                        initial=lambda params, **_: int(params.standard_load.target_load_per_fte),
                    ),
                    target_load_per_fte_calc=dict(
                        initial=lambda params, **_: int(params.standard_load.target_load_per_fte_calc) if params.standard_load.target_load_per_fte_calc else '',
                    )
                ),
                iommi_style=horizontal_fields_style,
                editable=False,
                actions__submit=None,
            )
        )
    )
    notes = Form(
        auto__model=StandardLoad, instance=lambda params, **_: params.standard_load,
        auto__include=[
            'notes'
        ],
        iommi_style=floating_fields_style,
        editable=False,
    )


class StandardLoadHistory(Page):
    """

    """
    header = HeaderInstanceHistory(
        lambda params, **_: params.standard_load.get_instance_header(),
    )
    table = Table(
        auto__model=StandardLoad,
        auto__include=['year', 'target_load_per_fte_calc'],
        rows=lambda params, **_: params.standard_load.history.all(),
        columns__history_date=dict(
            include=True,
            display_name="Date"
        ),
    )


urlpatterns = [
    path('load/<standard_load>/history/', StandardLoadHistory().as_view(), name='standard_load_history'),
    path('load/<standard_load>/edit/', StandardLoadEdit().as_view(), name='standard_load_edit'),
    path('load/<standard_load>/', StandardLoadDetail().as_view(), name='standard_load_detail'),
]
