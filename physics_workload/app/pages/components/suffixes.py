from iommi import Fragment, html


class SuffixCreate(Fragment):
    """
    Suffix for pages that create a file.
    """

    class Meta:
        tag = "span"
        attrs__class = {"text-success": True}
        children__text = " / Create "
        children__icon = html.i(
            attrs__class={"fa-solid": True, "fa-plus": True},
        )


class SuffixCreateTaskLead(Fragment):
    """
    Suffix for pages that create a unit lead post.
    """

    class Meta:
        tag = "span"
        attrs__class = {"text-success": True}
        children__text = " / Create Lead "
        children__icon = html.i(
            attrs__class={"fa-solid": True, "fa-user-plus": True},
        )


class SuffixCreateFullTime(Fragment):
    """
    Suffix for pages that create a full-time post.
    """

    class Meta:
        tag = "span"
        attrs__class = {"text-success": True}
        children__text = " / Create Full-Time "
        children__icon = html.i(
            attrs__class={"fa-solid": True, "fa-square-plus": True},
        )


class SuffixEdit(Fragment):
    """
    Suffix for pages that create a file.
    """

    class Meta:
        tag = "span"
        attrs__class = {"text-warning": True}
        children__text = " / Edit "

        children__icon = html.i(
            attrs__class={"fa-solid": True, "fa-pencil": True},
        )


class SuffixDelete(Fragment):
    """
    Suffix for pages that create a file.
    """

    class Meta:
        tag = "span"
        attrs__class = {"text-danger": True}
        children__text = " / Delete "
        children__icon = html.i(
            attrs__class={"fa-solid": True, "fa-trash": True},
        )


class SuffixHistory(Fragment):
    class Meta:
        tag = "span"
        attrs__class = {"text-secondary": True}
        children__text = " / History "
        children__icon = html.i(
            attrs__class={"fa-solid": True, "fa-clock-rotate-left": True},
        )
