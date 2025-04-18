# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path
from django.conf.urls import handler403
from app.pages.main_menu import main_menu
from app.pages.unit import urlpatterns as unit_urlpatterns
from app.pages.basic import PrivacyPage, PermissionDeniedPage, AboutPage
from app.pages.standard_load import urlpatterns as standard_load_urlpatterns
from app.views import home_view_redirect

urlpatterns = [
    # The home page
    path(
        '', home_view_redirect, name='home'
     ),
    path('about/', AboutPage().as_view(), name='about'),
    path('privacy/', PrivacyPage().as_view(), name='privacy'),
] + unit_urlpatterns + standard_load_urlpatterns + main_menu.urlpatterns()

# handler403 = PermissionDeniedPage().as_view()
