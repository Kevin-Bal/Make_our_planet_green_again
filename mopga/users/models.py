from django.db import models
from django.contrib.auth.models import User
from PIL import Image


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(default="default.png", upload_to="profile_pics")
    reputation = models.IntegerField(default=0)

    def __str__(self):
        return "{} Profile".format(self.user.username)

    # Remplace la méthode par défaut de model.save()
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        img = Image.open(self.avatar.path)

        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.avatar.path)

