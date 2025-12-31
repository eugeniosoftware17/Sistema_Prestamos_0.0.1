from django.urls import path
from . import views

urlpatterns = [
    # a /configuracion/ se mapea a esta vista.
    path('', views.gestionar_configuracion_impresion, name='configuracion_impresion'),
]
