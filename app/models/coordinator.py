from django.db.models import OneToOneField, PROTECT

from app.models.task import Task
from app.models.module_year import ModuleYear


class Coordinator(Task):
    """

    """
    module_year = OneToOneField(
        ModuleYear, verbose_name="Module Year", on_delete=PROTECT
    )


    class Meta:
        ordering = ('is_active', 'module', 'name',)
        verbose_name = 'Module Task'
        verbose_name_plural = 'Module Tasks'

    def __str__(self) -> str:
        return f"{self.module.code} - {self.name} ()"

    def get_absolute_url(self) -> str:
        return reverse_lazy('task_coordinator_detail', args=[self.pk])

    @property
    def load(self) -> float:
        if not self.load_calculated:
            self.calculate_load()

        return self.load_calculated

    @property
    def load_first(self) -> float:
        if not self.load_calculated_first:
            self.calculate_load()

        return self.load_calculated_first

    def calculate_load(self):
        """

        :return:
        """
        contact_sessions: int = self.lectures + self.synoptic_lectures + self.problem_classes

        load_lecture: float = contact_sessions * self.academic_year.load_lecture
        load_lecture_first: float = contact_sessions * self.academic_year.load_lecture_first

        load_coursework_set: float = self.coursework * self.academic_year.load_coursework_set
        load_coursework_credit: float = self.coursework * self.coursework_mark_fraction * self.credit_hours

        load_coursework_marked: float = (self.coursework + self.coursework_mark_fraction * self.credit_hours) * \
            self.coordinator_coursework_fraction * self.students * self.academic_year.load_coursework_marked

        load_exam_credit: float = self.exam_mark_fraction * self.credit_hours * self.academic_year.load_per_exam_credit
        load_exam_marked: float = self.students * self.coordinator_exam_fraction * self.academic_year.load_exam_marked

        load: float = self.load_fixed_coordinator + load_coursework_set + load_coursework_credit + \
                      load_exam_credit + load_exam_marked + load_coursework_marked

        if self.module.has_dissertation:
            if self.dissertation_load_function:
                load += self.dissertation_load_function.calculate(self.students)
            else:
                raise Exception("No dissertation load function")

        self.load_calculated_first = load + load_lecture_first
        self.load_calculated = load + load_lecture
        self.save()
