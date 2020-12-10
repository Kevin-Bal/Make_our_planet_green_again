from django.urls import path, include
from django.views.generic.base import RedirectView
from .views import home, projets


urlpatterns = [
    path('home', home, name="plateforme-view-home"),
    path('projets', projets, name="plateforme-view-projets"),
    path('', RedirectView.as_view(url='home')),
]