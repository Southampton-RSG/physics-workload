from logging import Logger, getLogger

from iommi import Form

from app.models import Unit
from app.utility import update_all_loads

logger: Logger = getLogger(__name__)


class UnitForm(Form):
    """
    Form for editing Modules
    """

    class Meta:
        auto__model = Unit
        auto__exclude = ["task_set"]
        fields__code__group = "Basics"
        fields__name__group = "Basics"
        fields__academic_group__group = "Basics"
        fields__academic_group__non_editable_input__template = "app/choice_url.html"
        fields__students__group = "Basics"
        fields__lectures__group = "Sessions"
        fields__problem_classes__group = "Sessions"
        fields__coursework__group = "Sessions"
        fields__synoptic_lectures__group = "Sessions"
        fields__exams__group = "Sessions"
        fields__credits__group = "Credit"
        fields__exam_mark_fraction__group = "Credit"
        fields__coursework_mark_fraction__group = "Credit"
        fields__has_dissertation__group = "Credit"
        fields__has_placement__group = "Credit"

        iommi_style = "floating_fields"

        @staticmethod
        def extra__on_delete(instance, **_):
            logger.info(f"Deleting module member {instance}")
            instance.delete()
            update_all_loads()

        @staticmethod
        def extra__on_save(form, instance, **_):
            logger.info(f"Editing module {instance}, as {form.extra.crud_type}")
            if instance.update_load():
                logger.info("Module changes require recalculation of global load target.")
                update_all_loads()
