from django.shortcuts import render
from .models import Projet



def home(request):
    return render(request, 'plateforme/home/home.html')

def projets(request):
    context = {
        'projets': Projet.objects.all()
    }
    return render(request, 'plateforme/projet/liste_projet.html', context)