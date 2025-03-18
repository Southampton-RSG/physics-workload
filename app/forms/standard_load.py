from logging import getLogger

from django.http import HttpResponseRedirect
from iommi import Form, Field

from app.models.standard_load import StandardLoad
from app.style import floating_fields_style
from app.assets import mathjax_js

logger = getLogger(__name__)


class StandardLoadForm(Form):

    class Meta:
        auto__model = StandardLoad
        assets=mathjax_js

        @staticmethod
        def actions__submit__post_handler(form, **_):
            """
            Make sure that we update the assignments if any of the task details change,
            and update the teaching hours calculation if that's then implied.

            :param form:
            :param _:
            :return:
            """
            logger.debug("Handling standard load form submission")
            if not form.is_valid():
                # This was an error
                logger.debug("Error in standard load form")
                return

            logger.debug("Submitted standard load form")

            # Get the new standard load, and try to get the old if it exists
            standard_load_new: StandardLoad = form.instance
            standard_load_old: StandardLoad = StandardLoad.objects.get(year=standard_load_new.year)

            form.apply(standard_load_new)
            standard_load_new.save()

            misc_hours_have_changed: bool = (standard_load_old.load_fte_misc == standard_load_new.load_fte_misc)

            if not standard_load_old:
                # This is a new year, so the total load hasn't changed
                logger.debug("New standard load year created")
                pass

            else:
                # The total load has changed, so we need to update the assignments
                assigned_load_has_changed: bool = False

                logger.debug("Updating existing load year")
                for task in standard_load_new.task_set.all():
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


class StandardLoadRefreshForm(Form):
    class Meta:
        auto__model = StandardLoad
        auto__include = ['year']

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

            standard_load: StandardLoad = form.instance

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

            return HttpResponseRedirect(standard_load.get_absolute_url())
