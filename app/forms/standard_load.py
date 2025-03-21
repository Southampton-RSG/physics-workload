from logging import getLogger

from django.http import HttpResponseRedirect, HttpResponse
from django.contrib import messages

from iommi import Form, Field, html, LAST

from app.models.standard_load import StandardLoad, get_current_standard_load
from app.assets import mathjax_js


logger = getLogger(__name__)


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
        def actions__submit__post_handler(form, **_) -> HttpResponse | None:
            """
            Make sure that we update the assignments if any of the task details change,
            and update the teaching hours calculation if that's then implied.

            :param form: The form returned.
            :return:
            """
            logger.debug("Handling standard load form submission")
            if not form.is_valid():
                # This was an error
                logger.debug("Error in standard load form")
                return None

            logger.debug("Submitted standard load form")

            # Get the new standard load, and try to get the old if it exists
            standard_load_new: StandardLoad = form.instance
            standard_load_old: StandardLoad = StandardLoad.objects.get(year=standard_load_new.year)

            form.apply(standard_load_new)
            standard_load_new.save()

            # Has this actually changed the misc load? That would require a reevaluation of teaching workload.
            misc_hours_have_changed: bool = (standard_load_old.load_fte_misc == standard_load_new.load_fte_misc)

            if not standard_load_old:
                # This is a new year, so the total load hasn't changed
                logger.debug("New standard load year created")

                # ENABLE HISTORY
                for staff in standard_load_old.staff_set.all():
                    staff.standard_load = standard_load_new
                    staff.save()

                for task in standard_load_old.task_set.all():
                    task.standard_load = standard_load_new
                    task.save()

                    # for assignment in task.assignment_set.all():


            # The total load has changed, so we need to update the assignments
            assigned_load_has_changed: bool = False

            logger.debug("Updating existing load year")
            for task in standard_load_new.task_set.all():
                # Step over all tasks, and see if the changes to this form have changed the total load
                logger.debug(f"Updating task {task}...")
                if task.update_load():
                    logger.debug(f"Updating task assignments...")
                    task.save()

                    for assignment in task.assignment_set.all():
                        logger.debug(f"Updating {assignment}...")
                        if assignment.update_load():
                            logger.debug(f"updating {assignment} staff...")
                            assigned_load_has_changed = True
                            assignment.save()
                            assignment.staff.update_load_assigned()
                            assignment.staff.save()

            if assigned_load_has_changed or misc_hours_have_changed:
                logger.debug("Updating standard load year with new assigned total")
                standard_load_new.update_target_load_per_fte()
                standard_load_new.save()

            return HttpResponseRedirect(standard_load_new.get_absolute_url())


class StandardLoadRecalculateForm(Form):
    """
    Form that's just a button that forces a full recalculate of the DB
    """
    class Meta:
        auto__model = StandardLoad
        auto__include = ['year']
        h_tag = None
        fields__year = Field.non_rendered(
            include=True,
            initial=lambda params, **_: params.standard_load.year,
        )
        actions__submit__display_name = "Re-calculate Loads"
        actions__submit__attrs__class = {"btn-warning": True}
        actions__submit__children__icon = html.i(
            attrs__class={'fa-solid': True, 'fa-cogs': True, 'ms-1': True}, after=LAST
        )

        @staticmethod
        def actions__submit__post_handler(form, params, **_) -> HttpResponse|None:
            """
            Make sure that we update the assignments if any of the task details change,
            and update the teaching hours calculation if that's then implied.

            :param form: The Iommi form.
            :param params: The params as seen by the Page.
            :return: Either back to the same page, or nowhere.
            """
            if not form.is_valid():
                # This was an error,
                return None

            standard_load: StandardLoad = params.standard_load

            for task in standard_load.task_set.all():
                task.update_load()
                task.save()

                for assignment in task.assignment_set.all():
                    assignment.update_load()
                    assignment.save()
                    assignment.staff.update_load_assigned()
                    assignment.staff.save()

            standard_load.update_target_load_per_fte()
            standard_load.save()

            messages.success("Re-calculated all loads from standards.")

            return HttpResponseRedirect(standard_load.get_absolute_url())

class StandardLoadNewYear(Form):
    """
    Form that's just a button that forces a full recalculate of the DB
    """
    class Meta:
        auto__model = StandardLoad
        auto__include = ['year']
        h_tag = None
        fields__year = Field.non_rendered(
            include=True,
            initial=lambda params, **_: params.standard_load.year,
        )
        actions__submit__display_name = "Re-calculate Loads"
        actions__submit__attrs__class = {"btn-warning": True}
        actions__submit__children__icon = html.i(
            attrs__class={'fa-solid': True, 'fa-cogs': True, 'ms-1': True}, after=LAST
        )

        @staticmethod
        def actions__submit__post_handler(form, params, **_) -> HttpResponse|None:
            """
            Make sure that we update the assignments if any of the task details change,
            and update the teaching hours calculation if that's then implied.

            :param form: The Iommi form.
            :param params: The params as seen by the Page.
            :return: Either back to the same page, or nowhere.
            """
            if not form.is_valid():
                # This was an error,
                return None

            standard_load: StandardLoad = params.standard_load

            for task in standard_load.task_set.all():
                task.update_load()
                task.save()

                for assignment in task.assignment_set.all():
                    assignment.update_load()
                    assignment.save()
                    assignment.staff.update_load_assigned()
                    assignment.staff.save()

            standard_load.update_target_load_per_fte()
            standard_load.save()

            messages.success("Re-calculated all loads from standards.")

            return HttpResponseRedirect(standard_load.get_absolute_url())

