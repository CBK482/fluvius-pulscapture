from django.http import HttpResponse
from django.views.generic import TemplateView

from django.template import loader
from django.shortcuts import render


# Create your views here.
index = TemplateView.as_view(template_name="index.html")
