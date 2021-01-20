from django.db import models

class Contact(models.Model):
    email = models.EmailField(max_length=200)
    sujet = models.CharField(max_length=200)
    message = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Contact"

    def __str__(self):
        return self.sujet + "-" +  self.email
