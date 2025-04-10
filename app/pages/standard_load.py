"""
Handles the views for the Standard Load
"""
from django.urls import path
from django.utils.html import format_html

from iommi import Page, Table, html, Form, Column, Header, Action

from app.models.standard_load import StandardLoad
from app.forms.standard_load import StandardLoadForm, StandardLoadFormNewYear
from app.pages.components import Equations
from app.pages.components.headers import HeaderInstanceEdit, HeaderInstanceHistory
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
            is_removed__include=False,
            target_load_per_fte_calc__include=False,
        ),
        editable=True
    )


class StandardLoadNewYear(Page):
    """
    Edit the standard load, to produce a new year
    """
    header = Header(
        lambda params, **_: format_html(
            params.standard_load.get_instance_header() + " / New Year <i class='text-success fa-solid fa-calendar'></i>",
        )
    )
    form = StandardLoadFormNewYear.create(
        instance=lambda params, **_: params.standard_load,
    )


class StandardLoadDetail(Page):
    """
    Shows details of the standard load
    """
    header = Header(
        lambda params, **_: params.standard_load.get_instance_header(),
        attrs__class={'position-relative': True},
        children__buttons=html.span(
            template='app/standard_load/standard_load_detail_buttons.html'
        )
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


urlpatterns = [
    path('load/<standard_load>/new/', StandardLoadNewYear().as_view(), name='standard_load_new'),
    path('load/<standard_load>/edit/', StandardLoadEdit().as_view(), name='standard_load_edit'),
    path('load/<standard_load>/', StandardLoadDetail().as_view(), name='standard_load_detail'),
    path('load/', StandardLoadList().as_view(), name='standard_load_list'),
]
