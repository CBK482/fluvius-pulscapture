from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("pulse_outputs/", views.list_pulse_outputs, name="pulse_outputs"),
    path("pulses/", views.list_pulses, name="pulses")
]