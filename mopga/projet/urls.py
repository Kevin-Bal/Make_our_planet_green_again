from django.urls import path, include
from .views import *

urlpatterns = [
    path('home', home, name="projet-view-home"),
    path('projets', projets, name="projet-view-projets"),
]