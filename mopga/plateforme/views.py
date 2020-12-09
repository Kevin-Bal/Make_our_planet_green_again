from django.shortcuts import render
from .models import Projet



def home(request):
    return render(request, 'home/home.html')

def projets(request):
    context = {
        'projets': Projet.objects.all()
    }
    return render(request, 'projet/liste_projet.html', context)