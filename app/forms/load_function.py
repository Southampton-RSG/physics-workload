from logging import getLogger, Logger

from simpleeval import simple_eval

from iommi import Form

from app.models import LoadFunction, StandardLoad
from app.style import floating_fields_style
from app.assets import mathjax_js


logger: Logger = getLogger(__name__)


class LoadFunctionForm(Form):
    """
    Form for editing Load Function
    """
    class Meta:
        h_tag = None
        assets = mathjax_js
        auto=dict(
            model=LoadFunction,
            exclude=['is_removed'],
        )
        fields=dict(
            plot_minimum=dict(
                group="Plot",
            ),
            plot_maximum=dict(
                group="Plot",
            )
        )
        iommi_style=floating_fields_style

        @staticmethod
        def fields__expression__is_valid(parsed_data, **_) -> (bool, str):
            """
            Tests to make sure the expression is valid!

            :param parsed_data: The inbound text.
            :raises ValidationError: If the expression is invalid.
            :return: True/False, and then the reason why it failed if false.
            """
            try:
                simple_eval(parsed_data, names={'s': 1})
            except Exception as e:
                return False, f"{e}"

            return True, ""

        @staticmethod
        def extra__post_validation(form, instance, **_):
            logger.debug(f"Validating Load Function during {form.extra.crud_type}")
            if form.extra.crud_type == 'delete':
                if instance.task_set.count():
                    form.add_error(
                        "You cannot delete a Load Function that is used by Tasks."
                    )

        @staticmethod
        def extra__on_save(form, instance, **_):
            logger.info(f"Editing load function {instance}, as {form.extra.crud_type}")

            if any(task.update_load() for task in instance.task_set.filter(is_removed=False).all()):
                logger.info(f"Load function changes require recalculation of global load target.")
                standard_load: StandardLoad = StandardLoad.objects.latest()
                standard_load.update_target_load_per_fte()
