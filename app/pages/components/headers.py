from iommi import Header, html


class HeaderInstanceEdit(Header):
    """
    A header for a model being edited
    """
    class Meta:
        children__suffix=html.span(template='app/edit_suffix.html')


class HeaderInstanceCreate(Header):
    """
    A header for a model being edited
    """
    class Meta:
        children__suffix=html.span(template='app/create_suffix.html')


class HeaderInstanceDelete(Header):
    """
    A header for a model being deleted
    """
    class Meta:
        children__suffix=html.span(template='app/delete_suffix.html')


class HeaderInstanceDetail(Header):
    """
    A header, with edit and delete buttons after it
    """
    class Meta:
        children__button=html.span(template='app/header/modify_button.html')
        attrs__class={'position-relative': True}


class HeaderInstanceDetailEdit(Header):
    """
    A header, with *only* an 'edit this model' button after it
    """
    class Meta:
        children__button=html.span(template='app/header/edit_button.html')
        attrs__class={'position-relative': True}


class HeaderInstanceHistory(Header):
    """
    A header without any extra buttons but with a time of deletion
    """
    class Meta:
        attrs__class={'position-relative': True}
        children__suffix=html.span(template='app/header/history_suffix.html')


class HeaderInstanceDetailDelete(Header):
    """
    A header, with *only* a 'delete this model' button after it
    """
    class Meta:
        children__button=html.span(template='app/header/delete_button.html')
        attrs__class={'position-relative': True}


class HeaderList(Header):
    """
    A header, with a 'create new' button after it
    """
    class Meta:
        children__button=html.span(template='app/header/create_button.html')
        attrs__class={'position-relative': True}
