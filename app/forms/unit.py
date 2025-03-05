from iommi import Form

from app.models.unit import Unit


class UnitForm(Form):
    """

    """
    class Meta:
        auto__model = Unit
        auto__exclude = ['is_active', 'task_set']
        fields__code__group = "Basics"
        fields__name__group = "Basics"
        fields__academic_group__group = "Basics"
        fields__academic_group__non_editable_input__template='app/choice_url.html'
        fields__students__group = 'Basics'
        fields__lectures__group = 'Sessions'
        fields__problem_classes__group = 'Sessions'
        fields__coursework__group = 'Sessions'
        fields__synoptic_lectures__group = 'Sessions'
        fields__exams__group = 'Sessions'
        fields__credits__group = 'Credit'
        fields__exam_mark_fraction__group = 'Credit'
        fields__coursework_mark_fraction__group = 'Credit'
        fields__has_dissertation__group = 'Credit'
        fields__has_placement__group = 'Credit'

        iommi_style = 'floating_fields'
