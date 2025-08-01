from iommi import Form, Header, Page

from app.assets import autosize_js
from app.models import Info
from app.pages.components.suffixes import SuffixEdit


class InfoForm(Form):
    class Meta:
        h_tag = (None,)
        instance = (lambda info, **_: info,)
        auto = dict(
            model=Info,
            exclude=["name", "page"],
        )
        fields__text__attrs__class = {
            "form-floating": False,
        }
        fields__text__input__attrs__class = {
            "autosize": True,
        }
        assets = autosize_js


class InfoEdit(Page):
    header = Header(
        lambda info, **_: info.get_instance_header(),
        children__header=SuffixEdit(),
    )
    form = InfoForm.edit(
        h_tag=None,
        instance=lambda info, **_: info,
        auto=dict(
            model=Info,
            exclude=["name", "page"],
        ),
        # fields__text=dict(
        #     attrs__class={
        #         "autosize": True,
        #         "form-floating": False,
        #     },
        #
        # ),
    )
