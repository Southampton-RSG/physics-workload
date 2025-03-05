from iommi import Form, Field

from app.models.staff import Staff
from app.style import floating_fields_style


class StaffForm(Form):
    class Meta:
        auto__model=Staff
        auto__exclude=['user', 'is_active']
        fields__account__group='row1'
        fields__name__group='row1'
        fields__academic_group__group='row1'
        fields__academic_group__non_editable_input__template='app/choice_url.html'
        fields__gender__group='row1'
        fields__type__group='row1'
        fields__fte_fraction__group='row2'
        fields__hours_fixed__group='row2'
        fields__load_calculated_target__group='row2'
        fields__load_calculated_assigned__group='row2'
        fields__load_calculated_balance__group='row2'
        fields__load_historic_balance__group='row2'
        iommi_style=floating_fields_style
