from django.db import models

# Create your models here.
class User(models.Model):
    username = models.CharField(max_length=20)
    password = models.CharField(max_length=20)
    email = models.EmailField(max_length=50)


class Project(models.Model):
    proj_name = models.CharField(max_length=30)
    user = models.ForeignKey(User)
    create_time = models.DateTimeField(auto_now=True)
    sourcelist = models.CharField(max_length=100)
    complete_proj = models.CharField(max_length=200)
class Instance(models.Model):
    name = models.CharField(max_length=30)
    available = models.BooleanField(default=True)
