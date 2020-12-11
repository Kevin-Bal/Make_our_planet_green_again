from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(default="default.png", upload_to="profile_pics")

    def __str__(self):
        return "{} Profile".format(self.user.username)

    # Remplace la méthode par défaut de model.save()
    def save(self):
        super().save()
        
        img = Image.open(self.avatar.path)

        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.avatar.path)

