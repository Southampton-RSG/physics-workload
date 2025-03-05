from iommi import Fragment

from app.pages import BasePage


class PrivacyPage(BasePage):
    """
    Contains the privacy statement
    """
    text = Fragment(template='app/basic/privacy.html')


class PermissionDeniedPage(BasePage):
    """
    Shown when a 403 error is encountered
    """
    text = Fragment(template='app/basic/permission_denied.html')
