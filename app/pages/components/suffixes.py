from typing import Dict

from iommi import Fragment, html


class SuffixCreate(Fragment):
    """
    Suffix for pages that create a file.
    """
    class Meta:
        tag = "span"
        text = " / Create "
        attrs__class ={"text-success": True}
        children__icon = html.i(
            attrs__class={"fa-solid": True, "fa-plus": True},
        )


class SuffixEdit(Fragment):
    """
    Suffix for pages that create a file.
    """
    class Meta:
        tag = "span"
        text = " / Edit "
        attrs__class ={"text-warning": True}
        children__icon = html.i(
            attrs__class={"fa-solid": True, "fa-pencil": True},
        )


class SuffixDelete(Fragment):
    """
    Suffix for pages that create a file.
    """
    class Meta:
        tag = "span"
        text = " / Delete "
        attrs__class ={"text-danger": True}
        children__icon = html.i(
            attrs__class={"fa-solid": True, "fa-trash": True},
        )


class SuffixHistory(Fragment):
    class Meta:
        tag = "span"
        text = " / History "
        attrs__class ={"text-secondary": True}
        children__icon = html.i(
            attrs__class={"fa-solid": True, "fa-clock-rotate-left": True},
        )

