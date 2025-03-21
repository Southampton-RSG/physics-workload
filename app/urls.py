# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path
from django.conf.urls import handler403
from app.pages.unit import urlpatterns as unit_urlpatterns
from app.pages.academic_group import urlpatterns as academic_group_urlpatterns
from app.pages.staff import urlpatterns as staff_urlpatterns
from app.pages.basic import PrivacyPage, PermissionDeniedPage, AboutPage
from app.pages.task import urlpatterns as task_urlpatterns
from app.pages.standard_load import urlpatterns as standard_load_urlpatterns
from app.pages.load_function import urlpatterns as load_function_urlpatterns
from app.views import home_view_redirect

urlpatterns = [
    # The home page
    path(
        '', home_view_redirect, name='home'
     ),
    path('about/', AboutPage().as_view(), name='about'),
    path('privacy/', PrivacyPage().as_view(), name='privacy'),
] + unit_urlpatterns + academic_group_urlpatterns + staff_urlpatterns + \
              task_urlpatterns + standard_load_urlpatterns + load_function_urlpatterns

# handler403 = PermissionDeniedPage().as_view()
