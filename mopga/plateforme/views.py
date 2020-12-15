from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Projet, Evaluation
from .decorators import allowed_users


# Liste des décorateurs (dans l'ordre) qui faut passer avant d'accéder à la view "ProjetCreateView"
decorators_projet_create_view = [login_required, allowed_users(allowed_groups=['Porteur'])]


def home(request):
    return render(request, 'plateforme/home/home.html')


class ProjetListView(ListView):
    model = Projet
    template_name = 'plateforme/projet/liste_projet.html'
    context_object_name = 'projets'
    ordering = ['-dateCreation']
    paginate_by = 3


class UserProjetListView(ListView):
    model = Projet
    template_name = 'plateforme/projet/liste_user_projet.html'
    context_object_name = 'projets'
    paginate_by = 3

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Projet.objects.filter(auteur=user).order_by('-dateCreation')
    


class ProjetDetailView(DetailView):
    model = Projet
    template_name = 'plateforme/projet/detail_projet.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        projet = get_object_or_404(Projet, pk=self.kwargs.get('pk'))
        context['evaluations'] = Evaluation.objects.filter(projet=projet).order_by('-dateEvaluation')
        return context


@method_decorator(decorators_projet_create_view, name='dispatch')
class ProjetCreateView(CreateView):
    model = Projet
    template_name = 'plateforme/projet/formulaire_projet.html'
    fields = ['titre','content']

    def form_valid(self, form):
        form.instance.auteur = self.request.user
        return super().form_valid(form)

@method_decorator(allowed_users(allowed_groups=['Porteur']), name='dispatch')
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

@method_decorator(allowed_users(allowed_groups=['Porteur']), name='dispatch')
class ProjetDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Projet
    template_name = 'plateforme/projet/confirmation_suppression_projet.html'
    success_url = '/projets'

    def test_func(self):
        projet = self.get_object()
        if self.request.user == projet.auteur:
            return True
        return False


class EvaluationCreateView(CreateView):
    model = Evaluation
    template_name = 'plateforme/projet/evaluation_projet.html'
    fields = ['note', 'commentaire']

    def form_valid(self, form):
        form.instance.evaluateur = self.request.user
        
        projet = get_object_or_404(Projet, pk=self.kwargs.get('pk'))
        form.instance.projet = projet 

        messages.success(self.request, "Merci d'avoir évalué le projet de {} !".format(projet.auteur.username))
        return super().form_valid(form)