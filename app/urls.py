# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path
from app.pages.unit import urlpatterns as unit_urlpatterns
from app.pages.academic_group import urlpatterns as academic_group_urlpatterns
from app.pages.staff import urlpatterns as staff_urlpatterns
from app.pages.main import IndexPage
from app.pages.basic import PrivacyPage
from app.pages.task import urlpatterns as task_urlpatterns
from app.pages.standard_load import urlpatterns as standard_load_urlpatterns

urlpatterns = [
    # The home page
    path('', IndexPage().as_view(), name='home'),
    path('privacy/', PrivacyPage().as_view(), name='privacy'),
] + unit_urlpatterns + academic_group_urlpatterns + staff_urlpatterns + task_urlpatterns + standard_load_urlpatterns
