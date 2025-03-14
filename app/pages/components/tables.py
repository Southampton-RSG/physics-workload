from iommi import Column, LAST


class ColumnModify(Column):
    """
    Creates a single column that contains buttons, as a buttongroup, to edit and delete the item on this row.
    """
    class Meta:
        # include=lambda request, **_: request.user.is_staff
        cell__value=lambda row, **_: row.get_absolute_url()
        cell__template='app/modify_row.html'
        header__attrs__class={'text-center': True}
        after=LAST

    @staticmethod
    def create(**kwargs) -> Column:
        """
        A bit superfluous, but this is a 'nicer' (IMO) version of the Iommi Column.edit and Column.delete standards.
        :return: Returns an instance of a Column with standardised Edit & Delete buttons
        """
        return Column(
            # include=lambda request, **_: request.user.is_staff,
            cell__value=lambda row, **_: row.get_absolute_url(),
            cell__template='app/modify_row.html',
            cell__attrs__class={'text-center': True},
            header__attrs__class={'text-center': True},
            sortable=False,
            after=LAST,
        )
