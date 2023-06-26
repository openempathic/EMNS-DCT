from django.db import models
from django.contrib.auth.models import User
import uuid

# from PIL import Image


class Profile(models.Model):
    user        = models.OneToOneField(User, on_delete=models.CASCADE)
    image       = models.ImageField(default='media/default.jpg', upload_to='media/profile_picks')
    status      = models.CharField(max_length=70, null=True, choices=(('Admin', 'Admin'), ('Actor', 'Actor'), ('Viewer', 'Viewer'), ('NLD', 'NLD')), default='Viewer' )
    gender      = models.CharField(max_length=70, null=True, choices=(('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')), default='Other')
    age         = models.IntegerField(default=0)
    healthcare  = models.CharField(max_length=70, null=True, choices=(('Psychologist', 'Psychologist'), ('Psychatrist', 'Psychatrist'), ('Other physician', 'Other physician')), default='I am not a healthcare professional')
    institute   = models.CharField(max_length=70, null=True, default='Other')
    experience  = models.IntegerField(default=0)

    def __str__(self) -> str:
        return f"{self.user.username} Profile"

    # def save(self, *args, **kwargs):
    #     super().save(*args, **kwargs)
        
    #     img = Image.open(self.image.path)

    #     if img.height > 300 or img.width > 300:
    #         output_size = (300, 300)
    #         img.thumbnail(output_size)
    #         img.save(self.image.path)
