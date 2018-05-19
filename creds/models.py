from django.db import models

# Create your models here.

class Files(models.Model):
    file_hashed = models.CharField(max_length=200, unique=True)

#    def __str__(self):
#        return str(self.id)
