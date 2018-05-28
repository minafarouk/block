from django.db import models

# Create your models here.

class Subscribe(models.Model):
    email = models.EmailField(max_length=70, unique= True)
