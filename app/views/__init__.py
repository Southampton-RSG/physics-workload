from django.http import HttpRequest, HttpResponseRedirect
from django.urls import reverse


def home_view_redirect(request: HttpRequest) -> HttpResponseRedirect:
    """
    Handles what the front page should look like for different users.
    If the user is logged in and not an admin, then redirect them to their staff page.

    :param request:
    :return:
    """
    if request.user.is_authenticated:
        if request.user.is_staff:
            return HttpResponseRedirect(reverse('about'))
        else:
            try:
                return HttpResponseRedirect(request.user.staff.get_absolute_url())
            except:
                return HttpResponseRedirect(reverse('about'))

    else:
        return HttpResponseRedirect(reverse('about'))
