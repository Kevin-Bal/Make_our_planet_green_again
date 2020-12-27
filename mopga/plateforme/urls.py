from django.urls import path, include
from django.views.generic.base import RedirectView
from .views import (
    home,
    ProjetListView,
    ProjetDetailView, 
    ProjetCreateView, 
    ProjetUpdateView, 
    ProjetDeleteView,
    EvaluationCreateView,
    EvaluationDeleteView,
    UserEvaluationListView,
    ContributionCreateView,
    UserContributionListView,
    ProjetCloturerView,
)


urlpatterns = [
    path('home', home, name="plateforme-view-home"),
    path('projets', ProjetListView.as_view(), name="plateforme-view-projets"),
    path('utilisateur/<str:username>/evaluations', UserEvaluationListView.as_view(), name="plateforme-view-evaluation-user"),
    path('utilisateur/<str:username>/contributions', UserContributionListView.as_view(), name="plateforme-view-contribution-user"),    
    path('projet/<int:pk>', ProjetDetailView.as_view(), name="plateforme-view-projet-details"),
    path('projet/nouveau', ProjetCreateView.as_view(), name="plateforme-view-creer-projet"),
    path('projet/<int:pk>/modification', ProjetUpdateView.as_view(), name="plateforme-view-modifier-projet"),
    path('projet/<int:pk>/suppression', ProjetDeleteView.as_view(), name="plateforme-view-supprimer-projet"),
    path('projet/<int:pk>/cloture', ProjetCloturerView.as_view(), name="plateforme-view-cloturer-projet"),
    path('projet/<int:pk>/evaluation', EvaluationCreateView.as_view(), name="plateforme-view-evaluer-projet"),
    path('projet/<int:pk>/contribution', ContributionCreateView.as_view(), name="plateforme-view-contribuer-projet"),
    path('evaluation/<int:pk>', EvaluationDeleteView.as_view(), name="plateforme-view-supprimer-evaluation"),
    path('', RedirectView.as_view(url='home')),
]