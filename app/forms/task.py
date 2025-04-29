from logging import getLogger

from iommi import Form, Field

from app.models import Task, StandardLoad
from app.style import floating_fields_style


logger = getLogger(__name__)


class TaskForm(Form):
    """
    Form for displaying and editing Tasks
    """
    class Meta:
        auto = dict(
            model=Task,
            exclude=[
                'load_calc', 'load_calc_first', 'is_removed',
                'academic_group', 'unit',
            ],
        )
        fields = dict(
            name__group="Basic",
            number_needed__group="Basic",
            load_fixed__group="Load",
            load_fixed_first=dict(
                group="Load",
            ),

            load_coordinator=dict(
                group="Calculation",
                include=lambda params, **_: params.task.unit if hasattr(params, 'task') else hasattr(params, 'unit'),
            ),
            load_function=dict(
                group="Calculation",
                non_editable_input__template = 'app/choice_url.html',
            ),
            students__group = "Calculation",
            coursework_fraction=dict(
                group="Calculation",
                include=lambda params, **_: params.task.unit if hasattr(params, 'task') else hasattr(params, 'unit'),
            ),
            exam_fraction=dict(
                group="Calculation",
                include=lambda params, **_: params.task.unit if hasattr(params, 'task') else hasattr(params, 'unit'),
            ),
        )
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
