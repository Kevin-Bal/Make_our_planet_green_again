from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse

class Projet(models.Model):
    titre = models.CharField(max_length=100)
    content = models.TextField()
    dateCreation = models.DateTimeField(default=timezone.now)
    auteur = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return ('{}'.format(self.titre))

    def get_absolute_url(self):
        return reverse("plateforme-view-projet-details", kwargs={"pk": self.pk})
    