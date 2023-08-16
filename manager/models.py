from django.db import models

# Create your models here.
class Manage(models.Model):
    x = models.IntegerField()
    created=models.DateTimeField(auto_now_add=True)