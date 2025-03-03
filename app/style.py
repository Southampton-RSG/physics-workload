from iommi import LAST, Asset
from iommi.evaluate import evaluate_strict
from iommi.style import Style, register_style
from iommi.style_base import select2_enhanced_forms
from iommi.style_bootstrap5 import bootstrap5_base
from iommi.style_font_awesome_6 import font_awesome_6
from typing import Dict, Any


# ==============================================================================
# Base style for the website
base_style = Style(
    bootstrap5_base,
    font_awesome_6,
    base_template="app/iommi_base.html",
    root__assets__custom_base_css=Asset.css(attrs__href="/static/css/custom-base.css"),
)
register_style('teaching_time_tool', base_style)
# ------------------------------------------------------------------------------
boolean_button_fields_style: Style = Style(
    base_style,
    Field=dict(
        shortcuts=dict(
            boolean=dict(
                attrs__class={
                    'form-check': False,
                    'mb-3': False,
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
            ),
        )
    )
)
register_style('boolean_buttons', boolean_button_fields_style)


# ==============================================================================-
# To get Bootstrap 5 floating fields, we need to add the right class to the form,
# and move the label: https://getbootstrap.com/docs/5.3/forms/floating-labels/
floating_fields: Dict[str, Any] = {
    "label__after": "input",
    "attrs": {
        "class": {"form-floating": True},
    }
}
# Applied on a per-field or per-form basis
floating_fields_style: Style = Style(
    boolean_button_fields_style,
    Form__assets__custom_floating_css=Asset.css(attrs__href="/static/css/custom-floating.css"),
    Field=dict(
        shortcuts=dict(
            text=floating_fields,
            textarea=floating_fields,
            number=floating_fields,
            integer=floating_fields,
            choice=floating_fields,
            choice_queryset=floating_fields,
        ),
        input__attrs__placeholder=lambda field, **_: evaluate_strict(
            field.display_name, **field.iommi_evaluate_parameters()
        ),
    )
)
register_style('floating_fields', floating_fields_style)
# ------------------------------------------------------------------------------

# ==============================================================================
# Used in forms to get horizontal fields; apply form-wide or per-field
# To get horizontal fields, we need to label the form rows and wrap the <input> in a div
horizontal_fields: Dict[str, Any] = {
    "attrs__class": {"col": False, "row": True},
    "template": "app/horizontal_field.html",
}
# Applied on a per-field or per-form basis, as an object or 'horizontal_fields'
horizontal_fields_style: Style = Style(
    base_style,
    Form__assets__custom_horizontal_css=Asset.css(attrs__href="/static/css/custom-horizontal.css"),
    Field=dict(
        shortcuts=dict(
            text=horizontal_fields,
            textarea=horizontal_fields,
            number=horizontal_fields,
            integer=horizontal_fields,
            choice=horizontal_fields,
            choice_queryset=horizontal_fields,
        ),
    )
)
register_style('horizontal_fields', horizontal_fields_style)
# ------------------------------------------------------------------------------

select2_fields_mixin_style: Style = Style(
    select2_enhanced_forms,
    Form__assets__custom_select2_css=Asset.css(attrs__href="/static/css/custom-select.css"),
)

# ==============================================================================
# validate_styles()
