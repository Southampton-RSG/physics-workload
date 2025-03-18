from django.http import HttpResponseRedirect
from iommi import Form

from app.models.unit import Unit


class UnitForm(Form):
    """
    Form for editing Units
    """
    class Meta:
        auto__model = Unit
        auto__exclude = ['is_active', 'task_set' , 'standard_load']
        fields__code__group = "Basics"
        fields__name__group = "Basics"
        fields__academic_group__group = "Basics"
        fields__academic_group__non_editable_input__template='app/choice_url.html'
        fields__students__group = 'Basics'
        fields__lectures__group = 'Sessions'
        fields__problem_classes__group = 'Sessions'
        fields__coursework__group = 'Sessions'
        fields__synoptic_lectures__group = 'Sessions'
        fields__exams__group = 'Sessions'
        fields__credits__group = 'Credit'
        fields__exam_mark_fraction__group = 'Credit'
        fields__coursework_mark_fraction__group = 'Credit'
        fields__has_dissertation__group = 'Credit'
        fields__has_placement__group = 'Credit'

        iommi_style = 'floating_fields'

    @staticmethod
    def actions__submit__post_handler(form, **_):
        """
        Make sure that we update the child tasks if any of the unit details change,
        and update the teaching hours calculation if that's then implied.

        :param form:
        :param _:
        :return:
        """
        if not form.is_valid():
            # This was an error,
            return

        unit_old: Unit = Unit.objects.get(pk=form.cleaned_data['pk'])
        unit_new: Unit = form.instance

        form.apply(unit_new)
        unit_new.save()

        if not unit_new:
            # This is a new unit, so the total load hasn't changed
            pass

        else:
            assignment_load_has_changed: bool = False

            for task in unit_new.task_set.all():
                task_old_load_calc = task.load_calc
                task_old_load_calc_first = task.load_calc_first
                task_load_has_changed: bool = task.update_load()

                if task_load_has_changed:
                    # If it actually has an effect, then flag that fact and update the task
                    task.save()

                    for assignment in task.assignment_set.all():
                        if assignment.update_load():
                            # If this has actually changed the assignment loads too, then update them and the staff
                            assignment_load_has_changed = True
                            assignment.save()
                            assignment.staff.update_load_assigned()
                            assignment.staff.save()

            if assignment_load_has_changed:
                # If we need to update the standard load, then do so
                unit_new.standard_load.update_target_load_per_fte()
                unit_new.standard_load.save()

        return HttpResponseRedirect('..')
