from django.http import HttpResponseRedirect
from iommi import Form

from app.models import Task
from app.style import floating_fields_style


class TaskForm(Form):
    """
    Form for editing Tasks
    """
    class Meta:
        auto__model = Task
        auto__exclude = ['is_active', 'load_calc', 'load_calc_first', 'standard_load']

        fields__name__group = "Basic"
        fields__number_needed__group = "Basic"

        fields__load_fixed__group = "Load"
        fields__load_fixed_first__group = "Load"

        fields__students__group = "Load Function"
        fields__load_function__group = "Load Function"

        fields__coursework_fraction__group = "Mark Fractions"
        fields__exam_fraction__group = "Mark Fractions"

        fields__load_calc__group = "Calculated Load"
        fields__load_calc_first__group = "Calculated Load"

        iommi_style = floating_fields_style

        @staticmethod
        def actions__submit__post_handler(form, **_):
            """
            Make sure that we update the assignments if any of the task details change,
            and update the teaching hours calculation if that's then implied.

            :param form:
            :param _:
            :return:
            """
            if not form.is_valid():
                # This was an error,
                return

            task_old: Task = Task.objects.get(pk=form.instance.pk)
            task_new: Task = form.instance

            form.apply(task_new)
            task_load_has_changed: bool = task_new.update_load()
            task_new.save()

            if not task_old:
                # This is a new task, so the total load hasn't changed
                pass
            elif task_load_has_changed:
                assignment_load_has_changed: bool = False

                # The total load has changed, so we need to update the assignments
                for assignment in task_new.assignment_set.all():
                    if assignment.update_load():
                        # If this has actually changed the assignment loads too, then update them and the staff
                        assignment_load_has_changed = True
                        assignment.save()
                        if assignment.staff.update_load_assigned():
                            assignment.staff.save()

                if assignment_load_has_changed:
                    # If the total assigned load changed, then update the standard load calculations
                    task_new.standard_load.update_target_load_per_fte()
                    task_new.standard_load.save()

            return HttpResponseRedirect('..')
