from django.urls import path, include
from django.views.generic.base import RedirectView
from .views import home, ProjetListView, ProjetDetailView, ProjetCreateView, ProjetUpdateView, ProjetDeleteView, UserProjetListView


urlpatterns = [
    path('home', home, name="plateforme-view-home"),
    path('projets', ProjetListView.as_view(), name="plateforme-view-projets"),
    path('utilisateur/<str:username>', UserProjetListView.as_view(), name="plateforme-view-projet-user"),   
    path('projet/<int:pk>', ProjetDetailView.as_view(), name="plateforme-view-projet-details"),
    path('projet/nouveau', ProjetCreateView.as_view(), name="plateforme-view-creer-projet"),
    path('projet/<int:pk>/modification', ProjetUpdateView.as_view(), name="plateforme-view-modifier-projet"),
    path('projet/<int:pk>/suppression', ProjetDeleteView.as_view(), name="plateforme-view-supprimer-projet"),
    path('', RedirectView.as_view(url='home')),
]