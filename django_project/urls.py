"""URL configuration for Django Ninja benchmark."""

from __future__ import annotations

from django.urls import path

from django_project.ninja_api import api

urlpatterns = [
    path("ninja/", api.urls),
]
