from datetime import datetime
from logging import getLogger, Logger

from django.conf import settings
from django.contrib import messages
from django.db.models import Sum
from django.http import HttpResponseRedirect, HttpResponse
from django.utils.timezone import localtime

from iommi import Form, Action, Field

from app.assets import mathjax_js
from app.models import Staff, Unit, LoadFunction, AcademicGroup, Assignment, Task, StandardLoad
from app.style import horizontal_fields_style, floating_fields_style


logger: Logger = getLogger(__name__)


class StandardLoadForm(Form):
    """
    Form for the Standard Load model
    """
    class Meta:
        """
        Includes mathjax for rendering the help text on the model
        """
        auto__model = StandardLoad
        assets=mathjax_js

        @staticmethod
        def actions__submit__post_handler(form, request, **_) -> HttpResponse | None:
            """
            Make sure that we update the assignments if any of the task details change,
            and update the teaching hours calculation if that's then implied.

            :param form: The form returned.
            :param request: The current request.
            :return:
            """
            logger.debug("Handling standard load form submission")
            if not form.is_valid():
                # This was an error
                logger.debug("Error in standard load form")
                return None

            logger.debug("Submitted standard load form")

            # Get the new standard load, and try to get the old from the DB if it exists
            standard_load_new: StandardLoad = form.instance
            standard_load_old: StandardLoad = StandardLoad.objects.get(pk=standard_load_new.pk)

            # We now have the 'old' in memory, and the 'new' in DB.
            # We need the 'new' in DB so that other models can see the updated values.
            form.apply(standard_load_new)
            standard_load_new.save()

            # Now, we trigger the update (if required)
            if standard_load_new.update_calculated_loads(standard_load_old):
                messages.success(
                    request,
                    "Updated loads with new values."
                )

            return HttpResponseRedirect(standard_load_new.get_absolute_url())


class StandardLoadFormNewYear(Form):
    """
    Form for the Standard Load model
    """

    class Meta:
        """
        Includes mathjax for rendering the help text on the model
        """
        auto=dict(
            model = StandardLoad,
            exclude = ['is_removed', 'target_load_per_fte_calc']
        )
        fields=dict(
            year=dict(
                editable=False,
                initial=lambda params, **_: params.standard_load.year + 1
            ),
            notes=dict(
                iommi_style=floating_fields_style
            )
        )
        h_tag = None
        actions__submit = dict(
            display_name="Save as new year",
            attrs__class={
                "btn-success": True,
            }
        )
        iommi_style = horizontal_fields_style
        assets = mathjax_js

        @staticmethod
        def actions__submit__post_handler(form, request, **_) -> HttpResponse | None:
            """
            If this is saved as a new year... then update everything!

            :param form: The form returned.
            :param request: The current request.
            :return:
            """
            logger.debug("Handling standard load form for new year")
            if not form.is_valid():
                # This was an error
                logger.debug("Error in standard load form")
                return None

            logger.debug("Submitted standard load form for new year successfully, so saving a timestamped version of all models.")

            # Get the new standard load form the form
            standard_load_new: StandardLoad = form.instance

            # ------------------------------------------------------------------
            # Save a timestamped version of all of the end-of-year models
            # ------------------------------------------------------------------
            settings.SIMPLE_HISTORY_ENABLED = True
            current_date: datetime = localtime()

            standard_load_old: StandardLoad = StandardLoad.objects.get(pk=standard_load_new.pk)
            standard_load_old._history_date = current_date
            standard_load_old.save()

            for staff in Staff.available_objects.all():
                staff.load_balance_final = staff.get_load_balance()
                staff._history_date = current_date
                staff.save()

            for assignment in Assignment.available_objects.all():
                assignment._history_date = current_date
                assignment.save()

            for task in Task.available_objects.all():
                task._history_date = current_date
                task.save()

            for unit in Unit.available_objects.all():
                unit._history_date = current_date
                unit.save()

            for load_function in LoadFunction.available_objects.all():
                load_function._history_date = current_date
                load_function.save()

            for academic_group in AcademicGroup.available_objects.all():
                academic_group._history_date = current_date
                academic_group.save()

            settings.SIMPLE_HISTORY_ENABLED = False

            # ------------------------------------------------------------------
            # Now we have a historical record, apply the new year and save it
            # ------------------------------------------------------------------
            form.apply(standard_load_new)
            standard_load_new.save()

            for staff in Staff.available_objects.all():
                staff.load_balance_historic = staff.history.aggregate(
                    Sum('load_balance_final')
                )['load_balance_final__sum']
                staff.load_balance_final = 0
                staff.save()

            for assignment in Assignment.available_objects.all():
                assignment.is_provisional = True
                assignment.save()

            # Now, we trigger the update (if required)
            if standard_load_new.update_calculated_loads(standard_load_old):
                messages.success(
                    request,
                    "Advanced to the next academic year."
                )

            return HttpResponseRedirect(
                standard_load_new.get_absolute_url()
            )
