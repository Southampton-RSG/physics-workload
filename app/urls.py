# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, re_path
from iommi import Form, EditTable
from iommi.views import crud_views

from app import views
from app.models import AcademicGroup, AcademicYear
from app.pages.module import urlpatterns as module_urlpatterns
from app.pages.academic_group import urlpatterns as academic_group_urlpatterns
from app.pages.staff import urlpatterns as staff_urlpatterns


urlpatterns = [
    # The home page
    path('', views.index, name='home'),

    path(
        'academic_group/list/',
        EditTable(
            auto__model=AcademicGroup,
            columns__name__field__include=True,
            columns__is_active__field__include=True,
            columns__is_active__filter__include=True,
            query__form__fields__is_active__initial=True,
        ).as_view(),
    ),

    path('year/', crud_views(model=AcademicYear), name='academic_year'),
                  # Matches any html file
    # re_path(
    #     r'^.*\.*',
    #     views.pages, name='pages'
    # ),

] + module_urlpatterns + academic_group_urlpatterns + staff_urlpatterns
