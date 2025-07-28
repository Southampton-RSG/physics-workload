from logging import Logger, getLogger

from iommi import Field, Form

from app.models import Task
from app.utility import update_all_loads

logger: Logger = getLogger(__name__)


class TaskForm(Form):
    """
    Task for module co-ordinators
    """
    class Meta:
        auto__model = Task

        @staticmethod
        def extra__on_delete(instance, **_):
            logger.info(f"Deleting task {instance}")
            instance.delete()
            update_all_loads()

        @staticmethod
        def extra__on_save(form, instance, **_):
            logger.info(f"Editing task {instance}, as {form.extra.crud_type}")
            if instance.update_load():
                logger.info("Task changes require recalculation of global load target.")
                update_all_loads()


class TaskDetailForm(TaskForm):
    class Meta:
        instance = lambda task, **_: task
        auto__exclude=[
            'name',
            'unit', 'academic_group',
            'load_fixed', 'load_fixed_first', 'load_multiplier',
            'description',
            'notes',
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
            is_full_time=dict(
                include=lambda task, **_: task.is_full_time,
                group="Calculated Load",
                after='is_required',
            ),
            is_lead=dict(
                include=lambda task, **_: task.is_lead,
                group="Calculated Load",
                after='is_full_time',
            ),
            is_unique=dict(
                include=lambda task, **_: task.is_unique,
                group="Calculated Load",
                after='is_lead',
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
        auto=dict(
            model=Task,
            exclude=[
                'unit', 'is_lead', 'coursework_fraction', 'exam_fraction', 'is_full_time',
                'load_calc', 'load_calc_first',
            ]
        )
        fields=dict(
            load_fixed__group="Load",
            load_fixed_first__group="Load",
            load_multiplier__group="Load",
            load_function__group="Calculation Details",
            students__group="Calculation Details",
            is_unique__group="Switches",
            is_required__group="Switches",
        )
        actions__submit__attrs__class={
            "btn-primary": False,
            "btn-success": True,
        }


class TaskEditForm(TaskForm):
    class Meta:
        h_tag=None
        instance=lambda task, **_: task
        auto__exclude=[
            'unit', 'academic_group',
            'load_calc', 'load_calc_first',
        ]
        fields=dict(
            is_unique__group="Basic",
            is_required__group="Basic",
            is_full_time=dict(
                include=lambda task, **_: task.is_full_time,
                group="Basic",
                editable=False,
                after='is_unique',
            ),

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
            load_fixed__include=lambda task, **_: not task.is_full_time,
            load_fixed_first__include=lambda task, **_: not task.is_full_time,
            load_multiplier__include=lambda task, **_: not task.is_full_time,

            load_function=dict(
                include=lambda task, **_: not task.is_lead and not task.is_full_time,
                group="Calculation Details",
            ),
            students=dict(
                include=lambda task, **_: not task.is_lead and not task.is_full_time,
                group="Calculation Details",
            ),
        )
        extra__redirect_to = '..'

        @staticmethod
        def extra__on_delete(instance, **_):
            logger.info(f"Deleting task {instance}")
            instance.delete()
            update_all_loads()

        @staticmethod
        def extra__on_save(form, instance, **_):
            logger.info(f"Editing task {instance}, as {form.extra.crud_type}")
            if instance.update_load():
                logger.info("Task changes require recalculation of global load target.")
                update_all_loads()


class UnitTaskLeadCreateForm(TaskForm):
    class Meta:
        h_tag = None
        auto__exclude = [
            'academic_group', 'load_function', 'students',
            'load_calc', 'load_calc_first', 'is_full_time',
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


class TaskFullTimeCreateForm(TaskForm):
    class Meta:
        h_tag=None
        auto__include=[
            'name', 'is_unique', 'is_required', 'is_full_time',
            'name', 'description',
        ]
        fields=dict(
            is_full_time=dict(
                group="Switches",
                initial=True,
                editable=False,
                after='is_unique',
            ),
            is_unique=dict(
                group="Switches",
                initial=True,
                editable=False,
            ),
            is_required__group="Switches",
        )
