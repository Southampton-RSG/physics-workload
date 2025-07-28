from typing import Any, Dict

from iommi import Asset
from iommi.evaluate import evaluate_strict
from iommi.style import Style, register_style
from iommi.style_base import select2_enhanced_forms
from iommi.style_bootstrap5 import bootstrap5
from iommi.style_font_awesome_6 import font_awesome_6

# ==============================================================================
# Base style for the website
# ==============================================================================
base_style = Style(
    bootstrap5,
    font_awesome_6,
    MainMenu__template="app/main_menu/main_menu.html",
    base_template="app/iommi_base.html",
    root__assets=dict(
        custom_font_css=Asset.css(
            attrs__href="//fonts.googleapis.com/css2?family=Roboto:ital,wght@0,300;0,400;0,700;1,400&amp;display=swap",
            attrs__media="all",
        ),
        custom_base_css=Asset.css(
            attrs__href="/static/css/custom-base.css"
        ),
        autosize_js = Asset.js(
            attrs__href="/static/js/autosize.js",
        ),
    ),
    Container__attrs__class={
        "mt-5": False,
        "mt-4": True,
    },
)
register_style('teaching_time_tool', base_style)


boolean_buttons: Dict[str, Any] = dict(
    attrs__class={
        'form-check': False,
        'mb-3': True,
        'h-100': True,
    },
    input__attrs__class={
        'form-check-input': False,
        'btn-check': True,
    },
    label__attrs__class={
        'btn': True,
        'w-100': True,
        'form-label': False,
        'form_label': False,
        'btn-lg': True,
        'btn-outline-primary': True,
    }
)

# ==============================================================================-
# To get Bootstrap 5 floating fields, we need to add the right class to the form,
# and move the label: https://getbootstrap.com/docs/5.3/forms/floating-labels/
# ==============================================================================
floating_fields: Dict[str, Any] = {
    'label__after': 'input',
    'attrs': {
        'class': {
            'form-floating': True,
            'mb-3': True
        },
    },
    'non_editable_input': {
        'attrs': {
            'class': {
                'form-control': False,
                'form-control-plaintext': True,
                'form-select': False,
                'mb-3': False
            },
        }
    }
}
# Applied on a per-field or per-form basis
floating_fields_style: Style = Style(
    base_style,
    select2_enhanced_forms,
    Form__assets__custom_floating_css=Asset.css(attrs__href="/static/css/custom-floating.css"),
    Form__assets__custom_floating_select2_css=Asset.css(attrs__href="/static/css/custom-floating-select2.css"),
    Field__shortcuts__text=floating_fields,
    Field__shortcuts__textarea=floating_fields,
    Field__shortcuts__number=floating_fields,
    Field__shortcuts__integer=floating_fields,
    Field__shortcuts__choice=floating_fields,
    Field__shortcuts__choice_queryset=floating_fields,
    Field__shortcuts__select=floating_fields,
    Field__input__attrs__placeholder=lambda field, **_: evaluate_strict(
        field.display_name, **field.iommi_evaluate_parameters()
    ),
    Field__shortcuts__boolean=boolean_buttons,
    Query__form__fields__freetext_search=floating_fields,
)
register_style('floating_fields', floating_fields_style)

floating_fields_select2_inline_style: Style = Style(
    base_style,
    select2_enhanced_forms,
    Form__assets__custom_floating_css=Asset.css(attrs__href="/static/css/custom-floating.css"),
    Form__assets__custom_select2_inline_css=Asset.css(attrs__href="/static/css/custom-select2-inline.css"),
    Field__shortcuts__text=floating_fields,
    Field__shortcuts__textarea=floating_fields,
    Field__shortcuts__number=floating_fields,
    Field__shortcuts__integer=floating_fields,
    Field__shortcuts__choice=floating_fields,
    Field__shortcuts__choice_queryset=floating_fields,
    Field__input__attrs__placeholder=lambda field, **_: evaluate_strict(
        field.display_name, **field.iommi_evaluate_parameters()
    ),
    Field__shortcuts__boolean=boolean_buttons,
    Query__form__fields__freetext_search=floating_fields,
)
register_style('floating_fields_select2_inline', floating_fields_select2_inline_style)

# ==============================================================================
# Used in forms to get horizontal fields; apply form-wide or per-field
# To get horizontal fields, we need to label the form rows and wrap the <input> in a div
# ==============================================================================
horizontal_fields: Dict[str, Any] = {
    "attrs__class": {"col": False, "row": True},
    "template": "app/horizontal_field.html",
}
# Applied on a per-field or per-form basis, as an object or 'horizontal_fields'
horizontal_fields_style: Style = Style(
    base_style,
    Form__assets__custom_horizontal_css=Asset.css(attrs__href="/static/css/custom-horizontal.css"),
    Field__shortcuts__text=horizontal_fields,
    Field__shortcuts__textarea=horizontal_fields,
    Field__shortcuts__number=horizontal_fields,
    Field__shortcuts__integer=horizontal_fields,
    Field__shortcuts__choice=horizontal_fields,
    Field__shortcuts__choice_queryset=horizontal_fields,
    Field__shortcuts__boolean=boolean_buttons,
)
register_style('horizontal_fields', horizontal_fields_style)


def get_balance_classes(balance: float) -> Dict[str, bool]:
    """
    Just a simple function to colour text on load balance.
    """
    return {
        'text-success': True if balance <= -1 else False,
        'text-danger': True if balance >= 1 else False,
    }

def get_balance_classes_form(balance: float) -> Dict[str, bool]:
    """
    Just a simple function to colour text on load balance, in a form.
    """
    return {
        'text-success': True if balance <= -1 else False,
        'text-danger': True if balance >= 1 else False,
        'form-control-plaintext': True,
    }