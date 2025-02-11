"""
Handles the views for the Academic Groups
"""
from django.urls import path
from django.utils.html import format_html
from django.template import Template

from iommi import Page, Table, html, Form, EditTable, Column
from iommi.path import register_path_decoding
from iommi import register_search_fields
from iommi.views import crud_views

from app.models import AcademicGroup, Staff, Module, ModuleYear, TaskYearModule


register_path_decoding(academic_group=lambda string, **_: AcademicGroup.objects.get(pk=int(string)))


# class AGStaffTable(Table):
#     class Meta:
#         auto__rows = Staff.objects.all().select_related('academic_group')


class ModuleTable(Table):
    """

    """
    @staticmethod
    def get_exam_coverage(row) -> float:
        module_year: ModuleYear = row.get_latest_year()
        if not module_year:
            return f"{0}%"
        else:
            return f"{module_year.get_exam_coverage()}%"

    @staticmethod
    def get_problem_class_coverage(row) -> float:
        module_year: ModuleYear = row.get_latest_year()
        if not module_year:
            return f"{0}%"
        else:
            return f"{module_year.get_problem_class_coverage()}%"

    @staticmethod
    def get_lecture_coverage(row) -> float:
        module_year: ModuleYear = row.get_latest_year()
        if not module_year:
            return f"{0}%"
        else:
            return f"{module_year.get_lecture_coverage()}%"

    @staticmethod
    def get_synoptic_lecture_coverage(row) -> float:
        module_year: ModuleYear = row.get_latest_year()
        if not module_year:
            return f"{0}%"
        else:
            return f"{module_year.get_synoptic_lecture_coverage()}%"

    @staticmethod
    def get_coursework_coverage(row) -> float:
        module_year: ModuleYear = row.get_latest_year()
        if not module_year:
            return f"{0}%"
        else:
            return f"{module_year.get_coursework_coverage()}%"

    @staticmethod
    def get_placement_coverage(row) -> float:
        module_year: ModuleYear = row.get_latest_year()
        if not module_year:
            return f"{0}%"
        else:
            return f"{module_year.get_placement_coverage()}%"

    @staticmethod
    def get_dissertation_coverage(row) -> float:
        module_year: ModuleYear = row.get_latest_year()
        if not module_year:
            return f"{0}%"
        else:
            return f"{module_year.get_dissertation_coverage()}%"


    class Meta:
        auto__model = Module
        columns__lecture = Column(
            group='Coverage',
            cell__value=lambda row, **_: ModuleTable.get_lecture_coverage(row)
        )
        columns__synoptic_lecture = Column(
            group='Coverage',
            cell__value=lambda row, **_: ModuleTable.get_synoptic_lecture_coverage(row)
        )
        columns__problem_class = Column(
            group='Coverage',
            cell__value=lambda row, **_: ModuleTable.get_problem_class_coverage(row)
        )
        columns__coursework = Column(
            group='Coverage',
            cell__value=lambda row, **_: ModuleTable.get_coursework_coverage(row)
        )
        columns__exam = Column(
            group='Coverage',
            cell__value=lambda row, **_: ModuleTable.get_exam_coverage(row)
        )
        columns__dissertation = Column(
            group='Coverage',
            cell__value=lambda row, **_: ModuleTable.get_dissertation_coverage(row)
        )
        columns__placement = Column(
            group='Coverage',
            cell__value=lambda row, **_: ModuleTable.get_placement_coverage(row)
        )

        @staticmethod
        def columns__name__cell__url(row, **_) -> str:
            return row.get_absolute_url()


class AcademicGroupPage(Page):
    """

    """
    title = html.h1(lambda params, **_: f"{params.academic_group}")
    staff = Table(
        auto__model=Staff, auto__exclude=['user', 'notes', 'is_active'],
        page_size=20,
        columns__name__cell__url=lambda row, **_: row.get_absolute_url(),
        rows=lambda params, **_: Staff.objects_active.filter(academic_group=params.academic_group)
    )
    modules = ModuleTable(
        auto__exclude=['notes', 'academic_group', 'is_active'],
        page_size=20,
        rows=lambda params, **_: Module.objects_active.filter(academic_group=params.academic_group),
    )


urlpatterns = [
    path('group/<academic_group>/', AcademicGroupPage().as_view(), name='academic_group_detail'),
    path('group/', crud_views(model=AcademicGroup)),
]
