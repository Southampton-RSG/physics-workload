# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, re_path
from iommi import Form, EditTable
from iommi.views import crud_views

from app.views.academic_group import AcademicGroupView
from app import views
from app.models import AcademicGroup, Module, StandardLoads
from app.pages.module import urlpatterns as module_urlpatterns
from app.pages.module import ModulePage

urlpatterns = [
    # The home page
    path('', views.index, name='home'),

    re_path(
        r'^transactions/(?:(?P<pk>\d+)/)?(?:(?P<action>\w+)/)?', views.TransactionView.as_view(),
            name='transactions',
    ),
    re_path(
        r'^academic_group/(?:(?P<pk>\d+)/)?(?:(?P<action>\w+)/)?', AcademicGroupView.as_view(),
        name='academic_group',
    ),


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

    path('standard_loads/', crud_views(model=StandardLoads))

    # Matches any html file
    # re_path(
    #     r'^.*\.*',
    #     views.pages, name='pages'
    # ),

] + module_urlpatterns
