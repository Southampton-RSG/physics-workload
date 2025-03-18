"""
Handles the views for the Standard Load
"""
from django.urls import path
from django.utils.html import format_html

from iommi import Page, Table, html, Form, Column, Header, Field

from app.models import standard_load
from app.models.standard_load import StandardLoad
from app.forms.standard_load import StandardLoadForm, StandardLoadRefreshForm
from app.pages.components import Equations
from app.pages.components.headers import HeaderInstanceEdit, HeaderInstanceDetail, HeaderList
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
        auto__exclude=['year'],
        iommi_style=horizontal_fields_style,
        fields__notes__iommi_style=floating_fields_style,
        editable=True,
        extra__redirect_to='..',
    )


class StandardLoadDetail(Page):
    """
    Shows details of the standard load
    """
    header = HeaderInstanceDetail(
        lambda params, **_: params.standard_load.get_instance_header()
    )
    assignment = html.p(
        children=dict(
            header=Header("Assignment Factors"),
            equation=Equations(
                template="app/standard_load/equation_assignment.html",
            ),
            form=Form(
                auto__model=StandardLoad, instance=lambda params, **_: params.standard_load,
                auto__exclude=['year', 'target_load_per_fte', 'load_fte_misc', 'notes', 'target_load_per_fte_calc'],
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
                auto__include=['load_fte_misc', 'target_load_per_fte', 'target_load_per_fte_calc'],
                fields__target_load_per_fte__initial=lambda params, **_: int(params.standard_load.target_load_per_fte),
                fields__target_load_per_fte_calc__initial=lambda params, **_: int(params.standard_load.target_load_per_fte_calc) if params.standard_load.target_load_per_fte_calc else '',
                iommi_style=horizontal_fields_style,
                editable=False,
                actions__submit=None,
            )
        )
    )
    notes = Form(
        auto__model=StandardLoad, instance=lambda params, **_: params.standard_load,
        auto__include=['notes'],
        iommi_style=floating_fields_style,
        editable=False,
    )
    form = StandardLoadRefreshForm.edit(
        h_tag=None, instance=lambda params, **_: params.standard_load,
        fields__year=Field.non_rendered(
            include=True,
            initial=lambda params, **_: params.standard_load.year,
        )
    )


class StandardLoadList(Page):
    """
    Page listing the standard load over history
    """
    header = HeaderList(
        lambda params, **_: StandardLoad.get_model_header(),
    )
    list = Table(
        h_tag=None,
        auto__model=StandardLoad,
        auto__include=['year'],
        columns__year__cell__value=lambda row, **_: f"{row.year} - {row.year+1}",
        columns__year__cell__url=lambda row, **_: row.get_absolute_url(),
        columns__edit=Column.edit(
            cell__url=lambda row, **_: f"{row.get_absolute_url()}edit/",
            include=lambda request, **_: request.user.is_staff,
        ),
    )



urlpatterns = [
    path('load/<standard_load>/edit/', StandardLoadEdit().as_view(), name='standard_load_edit'),
    path('load/<standard_load>/', StandardLoadDetail().as_view(), name='standard_load_detail'),
    path('load/', StandardLoadList().as_view(), name='standard_load_list'),
]
