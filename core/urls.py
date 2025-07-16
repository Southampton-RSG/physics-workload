from django.contrib import admin
from django.urls import path, include, re_path
import django_auth_adfs

urlpatterns = [
    path('django_plotly_dash/', include('django_plotly_dash.urls')),
    path('oauth2/', include('django_auth_adfs.urls')),
    re_path(r'^login$', django_auth_adfs.views.OAuth2LoginView.as_view(), name='login'),
    re_path(r'^logout$', django_auth_adfs.views.OAuth2LogoutView.as_view(), name='logout'),
    path('admin/', admin.site.urls),  # Django admin route
    path("", include("app.urls")),  # The actual website
]
