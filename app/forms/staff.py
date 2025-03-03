from iommi import Form

from app.models.staff import Staff


class StaffForm(Form):
    class Meta:
        auto__model=Staff
        auto__exclude=['user', 'is_active']
        fields__account__group='row1',
        fields__name__group='row1',
        fields__academic_group__group='row1',
        fields__gender__group='row1',
        fields__type__group='row1',
        fields__fte_fraction__group='row2'
        fields__fte_fraction__include=lambda params, **_: params.staff.fte_fraction
        fields__hours_fixed__group='row2',
        fields__hours_fixed__include=lambda params, **_: params.staff.hours_fixed
        fields__load_calculated_target__group='row2'
        fields__load_calculated_target__display_name='Current year load (target)'
        fields__load_calculated_assigned__group='row2'
        fields__load_calculated_assigned__display_name='Current year load (assigned)'
        fields__load_calculated_balance__group='row2'
        fields__load_calculated_balance__display_name='Current year load (balance)'
        fields__load_historic_balance__group='row2'
        fields__load_historic_balance__display_name='Historic balance'

        iommi_style='floating_fields'
