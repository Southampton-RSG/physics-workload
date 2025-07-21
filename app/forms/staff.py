from logging import Logger, getLogger

from iommi import Form

from app.models import Staff
from app.style import floating_fields_style
from app.utility import update_all_loads

logger: Logger = getLogger(__name__)


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
        fields__fte_fraction__group='row2'
        fields__hours_fixed__group='row2'
        iommi_style = floating_fields_style

        @staticmethod
        def extra__on_delete(instance, **_):
            logger.info(f"Deleting staff member {instance}")
            instance.delete()
            update_all_loads()

        @staticmethod
        def extra__on_save(form, instance, **_):
            logger.info(f"Editing staff member {instance}, as {form.extra.crud_type}")
            if instance.update_load_target():
                logger.info("Staff changes require recalculation of global load target.")
                update_all_loads()