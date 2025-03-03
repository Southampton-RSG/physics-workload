from iommi import Form, html

from app.models import Task
from app.style import floating_fields_style


class TaskForm(Form):
    class Meta:
        auto__model = Task
        auto__exclude = ['is_active', 'load_calc', 'load_calc_first']

        fields__name__group = "Basic"
        fields__number_needed__group = "Basic"

        fields__load_fixed__group = "Load"
        fields__load_fixed_first__group = "Load"

        fields__students__group = "Load Function"
        fields__load_function__group = "Load Function"

        fields__coursework_fraction__group = "Mark Fractions"
        fields__exam_fraction__group = "Mark Fractions"

        fields__load_calc__group = "Calculated Load"
        fields__load_calc_first__group = "Calculated Load"

        iommi_style = floating_fields_style
