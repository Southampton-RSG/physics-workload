"""
Handles the views for the Standard Load
"""
from django.db.models import Count, Sum
from django.urls import path
from django.utils.html import format_html, mark_safe
from django.template import Template

from iommi import Page, Table, html, Form, EditTable, Column, Action, Menu, Fragment, Header, Asset
from iommi.path import register_path_decoding
from iommi import register_search_fields
from iommi.views import crud_views

from app.models import AcademicGroup, Staff, Unit, Task, StandardLoad
from app.pages import BasePage, Equations
from app.pages.components.headers import HeaderInstanceEdit, HeaderInstanceDetail, HeaderList
from app.style import horizontal_fields_style, floating_fields_style
from app.assets import mathjax_js


register_path_decoding(standard_load=lambda string, **_: StandardLoad.objects.get(year=int(string)))


class StandardLoadEdit(BasePage):
    """
    Edit the standard load
    """
    header = HeaderInstanceEdit(
        lambda params, **_: format_html(params.standard_load.get_instance_header()),
    )
    detail_factors = Form.edit(
        h_tag=None,
        auto__model=StandardLoad, instance=lambda params, **_: params.standard_load,
        auto__exclude=['year'],
        iommi_style=horizontal_fields_style,
        fields__notes__iommi_style=floating_fields_style,
        editable=True,
        assets=mathjax_js,
        extra__redirect_to='..',
    )


class StandardLoadDetail(BasePage):
    """
    Shows details of the standard load
    """
    header = HeaderInstanceDetail(
        lambda params, **_: format_html(
            params.standard_load.get_instance_header()
        )
    )
    equation = Equations(
        template="app/standard_load/equation.html",
    )
    heading_factors = html.h2(
        "Equation Factors"
    )
    detail_factors = Form(
        auto__model=StandardLoad, instance=lambda params, **_: params.standard_load,
        auto__exclude=['year', 'hours_fte', 'load_fte_misc', 'notes'],
        iommi_style=horizontal_fields_style,
        editable=False,
    )
    heading_misc = html.h2(
        "Other Standards"
    )
    detail_misc = Form(
        auto__model=StandardLoad, instance=lambda params, **_: params.standard_load,
        auto__include=['hours_fte', 'load_fte_misc', 'notes'],
        iommi_style=horizontal_fields_style,
        fields__notes__iommi_style=floating_fields_style,
        editable=False,
    )


class StandardLoadList(BasePage):
    """
    Page listing the standard load over history
    """
    header = Header(
        lambda params, **_: format_html(
            StandardLoad.get_model_header(),
        ),
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
