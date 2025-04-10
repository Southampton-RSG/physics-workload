from logging import getLogger

from django.http import HttpResponseRedirect
from iommi import Form

from app.models import Task, StandardLoad
from app.style import floating_fields_style


logger = getLogger(__name__)


class TaskForm(Form):
    """
    Form for editing Tasks
    """
    class Meta:
        auto__model = Task
        auto__exclude = ['load_calc', 'load_calc_first', 'is_removed']

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
        def extra__on_delete(instance, **_):
            logger.info(f"Deleting task member {instance}")
            instance.delete()
            StandardLoad.objects.latest().update_target_load_per_fte()

        @staticmethod
        def extra__on_save(form, instance, **_):
            logger.info(f"Editing task {instance}, as {form.extra.crud_type}")
            if instance.update_load():
                logger.info(f"Task changes require recalculation of global load target.")
                StandardLoad.objects.latest().update_calculated_loads()
