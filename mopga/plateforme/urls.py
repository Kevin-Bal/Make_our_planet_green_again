from django.urls import path, include
from .views import *

urlpatterns = [
    path('home', home, name="plateforme-view-home"),
    path('projets', projets, name="plateforme-view-projets"),
]