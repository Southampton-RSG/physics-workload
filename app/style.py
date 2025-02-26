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
)
register_style('teaching_time_tool', base_style)
# ------------------------------------------------------------------------------

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
    base_style,
    # select2_enhanced_forms,
    root__assets__custom_css=Asset.css(attrs__href="/static/css/custom-floating.css"),
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

# ==============================================================================
# validate_styles()
