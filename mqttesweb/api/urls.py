from django.urls import path

from . import views

urlpatterns = [
    path('es-data', views.esGET, name='es'),
]
