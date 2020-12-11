from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Projet


def home(request):
    return render(request, 'plateforme/home/home.html')


class ProjetListView(ListView):
    model = Projet
    template_name = 'plateforme/projet/liste_projet.html'
    context_object_name = 'projets'
    ordering = ['-dateCreation']

class ProjetDetailView(DetailView):
    model = Projet
    template_name = 'plateforme/projet/detail_projet.html'

class ProjetCreateView(LoginRequiredMixin, CreateView):
    model = Projet
    template_name = 'plateforme/projet/formulaire_projet.html'
    fields = ['titre','content']

    def form_valid(self, form):
        form.instance.auteur = self.request.user
        return super().form_valid(form)

class ProjetUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Projet
    template_name = 'plateforme/projet/formulaire_projet.html'
    fields = ['titre','content']

    def form_valid(self, form):
        form.instance.auteur = self.request.user
        return super().form_valid(form)

    def test_func(self):
        projet = self.get_object()
        if self.request.user == projet.auteur:
            return True
        return False

class ProjetDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Projet
    template_name = 'plateforme/projet/confirmation_suppression_projet.html'
    success_url = '/projets'

    def test_func(self):
        projet = self.get_object()
        if self.request.user == projet.auteur:
            return True
        return False