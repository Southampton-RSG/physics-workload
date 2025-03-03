from django.contrib import admin
from django.urls import path, include  # add this

urlpatterns = [
    path('admin/', admin.site.urls),          # Django admin route
    path("", include("app.urls")),             # UI Kits Html files
    path('django_plotly_dash/', include('django_plotly_dash.urls')),
]
