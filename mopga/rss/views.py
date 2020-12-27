from django.contrib.syndication.views import Feed
from django.urls import reverse
from plateforme.models import Projet, Evaluation


class LatestProjetsFeed(Feed):
    title = "Nouveaux projets"
    link = "/projets"
    description = "Liste des nouveaux projets créés"

    def items(self):
        # Les 5 derniers projets créés
        return Projet.objects.order_by('-dateCreation')[:5]

    def item_title(self, item):
        return item.titre

    def item_description(self, item):
        return item.content



class LatestEvaluationsProjetFeed(Feed):

    def get_object(self, request, pk):
        return Projet.objects.get(pk=pk)

    def title(self, obj):
        return "Projet {} : Nouvelles évaluations".format(obj.titre)

    def link(self, obj):
        return obj.get_absolute_url()
    
    def description(self, obj):
        return "Nouvelles évaluations récemment postées sur le projet {}".format(obj.titre)

    def items(self, obj):
        # Les 10 derniers evaluations créés sur le projet 'obj'
        return Evaluation.objects.filter(projet=obj).order_by('-dateEvaluation')[:10]

    def item_title(self, item):
        return "Evaluation de {}".format(item.evaluateur.username)

    def item_description(self, item):
        return " {}/10 - {} ".format(item.note, item.commentaire)