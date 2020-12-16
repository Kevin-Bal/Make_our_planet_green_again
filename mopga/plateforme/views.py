from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User, Group
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from .models import Projet, Evaluation
from .decorators import allowed_users
from .forms import EvaluationForm

NB_PROJETS_DEVENIR_EVALUATEUR = 3

# Liste des décorateurs (dans l'ordre) qui faut passer avant d'accéder à la view "ProjetCreateView"
decorators_projet_create_view = [login_required, allowed_users(allowed_groups=['Porteur'])]

# Liste des décorateurs (dans l'ordre) qui faut passer avant d'accéder à la view "EvaluationCreateView"
decorators_evaluation_create_view = [login_required, allowed_users(allowed_groups=['Evaluateur'])]


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

        if not self.request.user.groups.filter(name='Evaluateur').exists():
            # Lorsque qu'un utilisateur à créé NB_PROJETS_DEVENIR_EVALUATEUR, il devient evaluateur
            projets = Projet.objects.filter(auteur=form.instance.auteur)
            if projets.count() + 1 >= NB_PROJETS_DEVENIR_EVALUATEUR:
                group = Group.objects.get(name='Evaluateur')
                self.request.user.groups.add(group)

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






class UserEvaluationListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Evaluation
    template_name = 'plateforme/projet/evaluation/liste_user_evaluation.html'
    context_object_name = 'evaluations'
    paginate_by = 5

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Evaluation.objects.filter(evaluateur=user).order_by('-dateEvaluation')
    
    def test_func(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        if self.request.user == user:
            return True
        return False


@method_decorator(decorators_evaluation_create_view, name='dispatch')
class EvaluationCreateView(CreateView):
    model = Evaluation
    template_name = 'plateforme/projet/evaluation/evaluation_projet.html'
    form_class=EvaluationForm

    def form_valid(self, form):
        form.instance.evaluateur = self.request.user
        
        projet = get_object_or_404(Projet, pk=self.kwargs.get('pk'))
        form.instance.projet = projet 

        messages.success(self.request, "Merci d'avoir évalué le projet de {} !".format(projet.auteur.username))
        return super().form_valid(form)


class EvaluationDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Evaluation
    template_name = 'plateforme/projet/evaluation/confirmation_suppression_evaluation.html'

    def get_success_url(self):
        evaluation = get_object_or_404(Evaluation, pk=self.kwargs.get('pk'))
        return reverse("plateforme-view-projet-details", kwargs={"pk": evaluation.projet.id})

    def test_func(self):
        evaluation = self.get_object()
        if self.request.user == evaluation.evaluateur:
            return True
        return False