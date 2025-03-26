from django.http import HttpResponseRedirect
from iommi import Form, Field


from app.models.staff import Staff
from app.style import floating_fields_style


class StaffForm(Form):
    """
    Form for editing Staff
    """
    class Meta:
        auto__model=Staff
        fields__account__group='row1'
        fields__name__group='row1'
        fields__academic_group__group='row1'
        fields__academic_group__non_editable_input__template = 'app/choice_url.html'
        fields__gender__group='row1'
        fields__type__group='row1'
        fields__fte_fraction__group='row2'
        fields__hours_fixed__group='row2'
        iommi_style = floating_fields_style

        @staticmethod
        def actions__submit__post_handler(form, **_):
            """
            Make sure that we update the staff member to have the correct load target,
            and update the teaching hours calculation if that's then implied.

            :param form:
            :param _:
            :return:
            """
            if not form.is_valid():
                # This was an error,
                return

            staff_old: Staff = Staff.available_objects.get(pk=form.instance.pk)
            staff_new: Staff = form.instance

            form.apply(staff_new)

            target_load_has_changed: bool = staff_new.update_load_target()
            staff_new.save()

            # So, did this change anything about the staff that would imply a need for recalculating the target teaching hours?
            if staff_old and target_load_has_changed:
                staff_new.standard_load.update_target_load_per_fte()
                staff_new.standard_load.save()

            return HttpResponseRedirect('..')
