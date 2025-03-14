from iommi import Fragment, html, Page


class PrivacyPage(Page):
    """
    Contains the privacy statement
    """
    text = Fragment(template='app/basic/privacy.html')


class PermissionDeniedPage(Page):
    """
    Shown when a 403 error is encountered
    """
    text = Fragment(template='app/basic/permission_denied.html')


class IndexPage(Page):
    title = html.h1("Teaching Time Tool")
    text = html.p("Select a thing")