from logging import getLogger, Logger

from iommi import Form, Field

from app.models import Task, StandardLoad
from app.style import floating_fields_style


logger: Logger = getLogger(__name__)


class TaskForm(Form):
    """
    Task for unit co-ordinators
    """
    class Meta:
        auto__model = Task

        @staticmethod
        def extra__on_delete(instance, **_):
            logger.info(f"Deleting co-ordinator task {instance}")
            instance.delete()
            StandardLoad.objects.latest().update_target_load_per_fte()

        @staticmethod
        def extra__on_save(form, instance, **_):
            logger.info(f"Editing co-ordinator task {instance}, as {form.extra.crud_type}")
            if instance.update_load():
                logger.info(f"Task changes require recalculation of global load target.")
                StandardLoad.objects.latest().update_calculated_loads()


class TaskDetailForm(TaskForm):
    class Meta:
        instance = lambda task, **_: task
        auto__exclude=[
            'name',
            'unit', 'academic_group', 'is_lead',
            'load_fixed', 'load_fixed_first', 'load_multiplier',
            'is_unique',
            'description',
            'notes',
            'is_removed',
        ]
        title = "Details"
        fields = dict(
            load_calc__group="Calculated Load",
            load_calc_first=dict(
                group="Calculated Load",
                include=lambda task, **_: task.load_calc_first != task.load_calc,
            ),
            is_required=dict(
                group="Calculated Load",
                after='load_calc_first',
            ),
            coursework_fraction=dict(
                include=lambda task, **_: task.is_lead,
                group="Calculation Details",
                after='is_required',
            ),
            exam_fraction=dict(
                include=lambda task, **_: task.is_lead,
                group="Calculation Details",
                after='coursework_fraction',
            ),
            load_function=dict(
                include=lambda task, **_: task.load_function,
                group="Calculation Details",
                after='exam_fraction',
            ),
            students=dict(
                include=lambda task, **_: task.load_function,
                group="Calculation Details",
                after='load_function',
            ),
        )
        editable = False


class TaskCreateForm(TaskForm):
    class Meta:
        h_tag=None
        instance=lambda task, **_: task
        auto__exclude=[
            'is_removed',
            'unit', 'is_lead', 'coursework_fraction', 'exam_fraction'
            'load_calc', 'load_calc_first',
        ]
        fields=dict(
            load_fixed__group="Load",
            load_fixed_first__group="Load",
            load_multiplier__group="Load",
            load_function__group="Calculation Details",
            students__group="Calculation Details",
            is_unique__group="Switches",
            is_required__group="Switches",
        )


class TaskEditForm(TaskForm):
    class Meta:
        h_tag=None
        instance=lambda task, **_: task
        auto__exclude=[
            'is_removed',
            'unit', 'academic_group',
            'load_calc', 'load_calc_first',
        ]
        fields=dict(
            is_unique__group="Basic",
            is_required__group="Basic",

            load_fixed__group="Load",
            load_fixed_first__group="Load",
            load_multiplier__group="Load",

            is_lead=dict(
                include=lambda task, **_: task.is_lead,
                group="Calculation Details",
                editable=False,
            ),
            coursework_fraction=dict(
                include=lambda task, **_: task.is_lead,
                group="Calculation Details",
            ),
            exam_fraction=dict(
                include=lambda task, **_: task.is_lead,
                group="Calculation Details",
            ),
            load_function=dict(
                include=lambda task, **_: not task.is_lead,
                group="Calculation Details",
            ),
            students=dict(
                include=lambda task, **_: not task.is_lead,
                group="Calculation Details",
            ),
        )


class UnitTaskLeadCreateForm(TaskForm):
    class Meta:
        h_tag = None
        auto__exclude = [
            'is_removed',
            'academic_group', 'load_function', 'students',
            'load_calc', 'load_calc_first',
        ]
        fields = dict(
            name=dict(
                initial="Unit Lead",
                group="Basic",
            ),
            is_unique=dict(
                group='Basic',
                initial=True,
            ),
            is_required=dict(
                group='Basic',
                initial=True,
            ),

            unit=Field.non_rendered(
                initial=lambda unit, **_: unit,
            ),
            load_fixed__group="Load",
            load_fixed_first__group="Load",
            load_multiplier__group="Load",

            is_lead=Field.non_rendered(
                initial=True,
            ),
            coursework_fraction__group="Calculation",
            exam_fraction__group="Calculation",

            description=dict(
                initial="Leads/co-ordinates Unit."
            )
        )


class UnitTaskCreateForm(TaskForm):
    class Meta:
        h_tag = None
        auto__exclude = [
            'is_removed',
            'academic_group',
            'is_lead', 'coursework_fraction', 'exam_fraction',
            'load_calc', 'load_calc_first',
        ]
        fields = dict(
            name__group="Basic",
            is_unique__group='Basic',
            is_required__group='Basic',

            unit=Field.non_rendered(
                initial=lambda params, **_: params.unit,
                include=True,
            ),
            load_fixed__group="Load",
            load_fixed_first__group="Load",
            load_multiplier__group="Load",

            load_function__group="Calculation",
            students__group="Calculation",
        )