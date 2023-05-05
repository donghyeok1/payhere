from . import views
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("signup/", views.SignupView.as_view(), name='signup'),
]
