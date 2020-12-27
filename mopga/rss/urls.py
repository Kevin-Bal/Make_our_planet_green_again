from django.urls import path
from .views import LatestProjetsFeed, LatestEvaluationsProjetFeed


urlpatterns = [
    path('projets/<int:pk>/evaluations', LatestEvaluationsProjetFeed(), name="rss-evaluations-projets-news"),
    path('projets', LatestProjetsFeed(), name="rss-projets-news"),
]