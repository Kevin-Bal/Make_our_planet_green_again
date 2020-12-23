from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User, Group
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.db.models import Max
from .models import Projet, Evaluation, Contribution
from .decorators import allowed_users
from .forms import EvaluationForm
from users.models import Profile

NB_POINTS_REPUTATION_CREATION_PROJET = 20;

# Liste des décorateurs (dans l'ordre) qui faut passer avant d'accéder à la view "ProjetCreateView"
decorators_projet_create_view = [login_required, allowed_users(allowed_groups=['Porteur'])]

# Liste des décorateurs (dans l'ordre) qui faut passer avant d'accéder à la view "EvaluationCreateView"
decorators_evaluation_create_view = [login_required, allowed_users(allowed_groups=['Evaluateur'])]


def home(request):
    dernier_projet_cree = Projet.objects.filter().latest("dateCreation")
    dernier_projet_finance = None # A FAIRE
    profil_best_reputation = Profile.objects.all().order_by("-reputation").first()

    context = {
        'dernier_projet_cree': dernier_projet_cree,
        'dernier_projet_finance': dernier_projet_finance,
        'profil_best_reputation': profil_best_reputation
    }
    return render(request, 'plateforme/home/home.html', context)


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
    fields = ['titre','content','montantVoulu']

    def form_valid(self, form):
        form.instance.auteur = self.request.user

        # Mise à jour de la reputation de l'auteur
        maj_reputation_to_user(form.instance.auteur, form.instance.auteur.profile.reputation + NB_POINTS_REPUTATION_CREATION_PROJET)

        return super().form_valid(form)

class ProjetUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Projet
    template_name = 'plateforme/projet/formulaire_projet.html'
    fields = ['titre','content','montantVoulu']

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

        # Un utilisateur ne peut pas s'auto evaluer
        if form.instance.evaluateur != form.instance.projet.auteur:

            # Mise à jour de la reputation de l'auteur du projet
            # Il gagne ou perd de la reputation en fonction de la note 
            # ex : Pour une note de 10, il gagne 5 points, pour 9 il gagne 4 points, ... pour 0 il perd 5 points.
            points_reputation = form.instance.note - 5; # 5 car la note est sur 10
            maj_reputation_to_user(projet.auteur, projet.auteur.profile.reputation + points_reputation)

            messages.success(self.request, "Merci d'avoir évalué le projet de {} !".format(projet.auteur.username))
            return super().form_valid(form)
        else:
            messages.warning(self.request, "Vous ne pouvez pas vous auto-evaluer !")
            return super().form_invalid(form)


class EvaluationDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Evaluation
    template_name = 'plateforme/projet/evaluation/confirmation_suppression_evaluation.html'

    def get_success_url(self):
        evaluation = get_object_or_404(Evaluation, pk=self.kwargs.get('pk'))

        # Mise à jour de la reputation de l'auteur du projet
        # Il re-gagne ou re-perd de la reputation en fonction de la note qui va être supprimée 
        # ex : Pour une note de 10, on lui enleve les 5 points, pour 9 on lui enleve 4 points ... pour 0 il lui redonne 5 points.
        points_reputation = 5 - evaluation.note; # 5 car la note est sur 10
        maj_reputation_to_user(evaluation.projet.auteur, evaluation.projet.auteur.profile.reputation + points_reputation)

        return reverse("plateforme-view-projet-details", kwargs={"pk": evaluation.projet.id})

    def test_func(self):
        evaluation = self.get_object()
        if self.request.user == evaluation.evaluateur:
            return True
        return False


# Fonction qui met à jour la reputation d'un 'user' 
# puis qui verifie la condition pour être 'Evaluateur' (reputation > 0)
def maj_reputation_to_user(user, reputation):
    Profile.objects.filter(user=user).update(reputation=reputation)

    group = Group.objects.get(name='Evaluateur')
    if not user.groups.filter(name='Evaluateur').exists():
        if reputation > 0:
            user.groups.add(group)
    else:
        if reputation <= 0:
            user.groups.remove(group)
    

@method_decorator(decorators_evaluation_create_view, name='dispatch')
class ContributionCreateView(CreateView):
    model = Contribution
    template_name = 'plateforme/projet/contribution/contribution_projet.html'
    fields = ['montantContribution']

    def form_valid(self, form):
        form.instance.contributeur = self.request.user
        projet = get_object_or_404(Projet, pk=self.kwargs.get('pk'))
        form.instance.projet = projet

        # Mise à jour de la reputation du contributeur
        maj_reputation_to_user(form.instance.contributeur, projet.auteur.profile.reputation + 10)
        # Mise à jour du montant du projet
        maj_montant_to_projet(projet.id, projet.montant + form.instance.montantContribution)

        messages.success(self.request, "Merci d'avoir contribué de {} au projet de {} !".format(form.instance.montantContribution, projet.auteur.username))
        return super().form_valid(form)

class UserContributionListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Contribution
    template_name = 'plateforme/projet/contribution/liste_user_contribution.html'
    context_object_name = 'contributions'
    paginate_by = 5

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Contribution.objects.filter(contributeur=user).order_by('-dateContribution')
    
    def test_func(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        if self.request.user == user:
            return True
        return False

def maj_montant_to_projet(projetId, montant):
    Projet.objects.filter(id=projetId).update(montant=montant)
