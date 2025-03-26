from logging import getLogger

from django.http import HttpResponseRedirect, HttpResponse
from django.contrib import messages

from iommi import Form

from app.models.standard_load import StandardLoad
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
        def actions__submit__post_handler(form, request, **_) -> HttpResponse | None:
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
