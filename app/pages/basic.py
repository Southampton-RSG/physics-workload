from iommi import Fragment, html, Page, Header


class PrivacyPage(Page):
    """
    Contains the privacy statement
    """
    text = Fragment(
        template='app/basic/privacy.html'
    )


class AboutPage(Page):
    title = Header(
        "Teaching Time Tool"
    )
    text = html.p(
        "This is a web app for assigning and balancing teaching workload for staff in the University of Southampton's Department of Physics."
    )
