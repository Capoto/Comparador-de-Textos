from django.urls import path,include
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("plenario", views.plenario, name="plenario"),
    path("comissao", views.comissao, name="comissao"),
     path("index", views.index, name="index"),
]