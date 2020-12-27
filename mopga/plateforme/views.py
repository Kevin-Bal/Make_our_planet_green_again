from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User, Group
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from django.db.models import Max
from datetime import datetime
from django.utils.dateparse import parse_date
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
    if Projet.objects.all().exists() == True:
        dernier_projet_cree = Projet.objects.filter().latest("dateCreation")

        if Projet.objects.filter(estFinance=True).exists() == True:
            dernier_projet_finance = Projet.objects.filter(estFinance=True).latest("dateFinancement")
        else:
            dernier_projet_finance = None
    else:
        dernier_projet_finance = None  
        dernier_projet_cree = None
           
    
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
    paginate_by = 3

    # Variables pour sauvegarder les parametres de l'url pour conserver les filtres à chaque rechargement de la page
    URL_PARAM_FILTRE_TITRE = ''
    URL_PARAM_FILTRE_AUTEUR = ''
    URL_PARAM_FILTRE_DATE_CREATION = ''

    def get_queryset(self):
        projets = Projet.objects.all()

        # Application des filtres (+ sauvegarde des filtres) #
        titre = self.request.GET.get('titre')
        if titre:
            self.URL_PARAM_FILTRE_TITRE = titre
            projets = projets.filter(titre__icontains=titre)
        else:
            self.URL_PARAM_FILTRE_TITRE = ''

        username_auteur = self.request.GET.get('auteur')
        if username_auteur and username_auteur != 'Tous':
            self.URL_PARAM_FILTRE_AUTEUR = username_auteur
            auteur =  get_object_or_404(User, username=username_auteur)
            projets = projets.filter(auteur=auteur)
        else:
            self.URL_PARAM_FILTRE_AUTEUR = ''

        date_creation = self.request.GET.get('dateCreation')
        if date_creation:
            date = parse_date(date_creation)
            self.URL_PARAM_FILTRE_DATE_CREATION = date_creation
            projets = projets.filter(dateCreation__contains=date)
        else:
            self.URL_PARAM_FILTRE_DATE_CREATION = ''
        # Fin application des filtres #


        projets = projets.order_by('-dateCreation')
        return projets

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['users'] = User.objects.all()

        # Recuperation des parametres de l'url pour conserver les filtres à chaque rechargement de la page
        param_url = "?"
        if self.URL_PARAM_FILTRE_TITRE != '':
            param_url += "titre=" + self.URL_PARAM_FILTRE_TITRE + "&"
        if self.URL_PARAM_FILTRE_AUTEUR != '':
            param_url += "auteur=" + self.URL_PARAM_FILTRE_AUTEUR + "&"
        if self.URL_PARAM_FILTRE_DATE_CREATION != '':
            param_url += "dateCreation=" + self.URL_PARAM_FILTRE_DATE_CREATION + "&"
        context['parametres_url'] = param_url

        # Permet de pré-remplir les filtres avec les valeurs dans l'url
        context['filtre_titre'] = self.URL_PARAM_FILTRE_TITRE
        context['filtre_auteur'] = self.URL_PARAM_FILTRE_AUTEUR
        context['filtre_date_creation'] = self.URL_PARAM_FILTRE_DATE_CREATION

        return context        
    

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
        if Contribution.objects.filter(projet_id=projet.id).exists():
            for contribution in Contribution.objects.filter(projet_id=projet.id):
                user = contribution.contributeur
                maj_porteMonnaie_to_user(user, user.profile.porteMonnaie + contribution.montantContribution)

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
    

class ContributionCreateView(LoginRequiredMixin, CreateView):
    model = Contribution
    template_name = 'plateforme/projet/contribution/contribution_projet.html'
    fields = ['montantContribution']

    def form_valid(self, form):
        form.instance.contributeur = self.request.user
        projet = get_object_or_404(Projet, pk=self.kwargs.get('pk'))
        form.instance.projet = projet
        user = form.instance.contributeur

        if form.instance.contributeur.profile.porteMonnaie >=  form.instance.montantContribution:

            # Mise à jour de la reputation du contributeur
            maj_reputation_to_user(user, user.profile.reputation + 5)
            # Mise à jour du porte monnaie du contributeur
            maj_porteMonnaie_to_user(user, user.profile.porteMonnaie - form.instance.montantContribution)
            # Mise à jour du montant du projet
            maj_montant_to_projet(projet.id, projet.montant + form.instance.montantContribution)

            # On ajoute le user dans le groupe des contributeur, seulement si ce dernier ne l'est pas déjà
            group = Group.objects.get(name='Contributeur')
            if not user.groups.filter(name='Contributeur').exists():
                    user.groups.add(group)

            messages.success(self.request, "Merci d'avoir contribué de {} mopga-coin au projet de {} !".format(form.instance.montantContribution, projet.auteur.username))
            return super().form_valid(form)
        else :
            messages.error(self.request, "Le solde de votre porte-monnaie est insufisant !")
            return super().form_invalid(form)

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

# Cette méthode met à jour le montant du financement et quand ce dernier a atteind le montant voulu met à jour la date de financement
def maj_montant_to_projet(projetId, montant):
    Projet.objects.filter(id=projetId).update(montant=montant)
    projet_contribue = Projet.objects.get(id=projetId)

    # On met à jour la date de fianancement du projet quand celui-ci à atteind le montant voulu et qu'il n'a pas encore été financé
    if projet_contribue.montantVoulu <= projet_contribue.montant and projet_contribue.estFinance == 0 :
        projet_contribue.save()
        Projet.objects.filter(id=projetId).update(estFinance=True)
        

def maj_porteMonnaie_to_user(user, porteMonnaie):
    Profile.objects.filter(user=user).update(porteMonnaie=porteMonnaie)


