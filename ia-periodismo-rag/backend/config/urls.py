"""
URL configuration for config project.
"""
from django.contrib import admin
from django.urls import path, include
from portal import views as portal_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', portal_views.home_view, name='home'),
    path('api/', include('assistant.urls')),
]
