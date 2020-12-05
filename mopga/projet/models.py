from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class Projet(models.Model):
    titre = models.CharField(max_length=100)
    content = models.TextField()
    dateCreation = models.DateTimeField(default=timezone.now)
    auteur = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return ('{}'.format(self.titre))