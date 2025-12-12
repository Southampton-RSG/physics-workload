from django.http import HttpRequest, HttpResponse, HttpResponseRedirect


def home_redirect(request: HttpRequest) -> HttpResponse:
    """
    Redirects a logged-in user to their staff page.

    :param request: The request.
    :return: A redirect to their staff page.
    """
    return HttpResponseRedirect(request.user.staff.get_absolute_url())
