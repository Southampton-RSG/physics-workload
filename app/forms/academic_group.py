from iommi import Field, Form

from app.models import AcademicGroup
from app.style import floating_fields_style, get_balance_classes_form


class AcademicGroupDetailForm(Form):
    class Meta:
        auto=dict(
            model=AcademicGroup,
            exclude=[
                'code', 'short_name', 'name', 'load_balance_final',
            ]
        )
        fields=dict(
            load_balance=Field.integer(
                display_name="Load Balance",
                group="Row",
                initial=lambda academic_group, **_: academic_group.get_load_balance(),
                non_editable_input__attrs__class=lambda field, **_: get_balance_classes_form(field.value),
            ),
            load_balance_historic=dict(
                group="Row",
                non_editable_input__attrs__class=lambda field, **_: get_balance_classes_form(field.value),
            ),
        )
        editable=False
        include=lambda request, **_: request.user.is_staff
        instance=lambda academic_group, **_: academic_group

        iommi_style = floating_fields_style
