# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path
from app.pages.module import urlpatterns as module_urlpatterns
from app.pages.academic_group import urlpatterns as academic_group_urlpatterns
from app.pages.staff import urlpatterns as staff_urlpatterns
from app.pages.main import IndexPage

urlpatterns = [
    # The home page
    path('', IndexPage().as_view(), name='home'),
] + module_urlpatterns + academic_group_urlpatterns + staff_urlpatterns
