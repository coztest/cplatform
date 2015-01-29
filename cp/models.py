from django.db import models

# Create your models here.
class User(models.Model):
    username = models.CharField(max_length=20)
    password = models.CharField(max_length=20)
    email = models.EmailField(max_length=50)


class Project(models.Model):
    proj_name = models.CharField(max_length=30)
    user = models.ForeignKey(User)
    begin_time = models.DateTimeField(auto_now=True)
    end_time = models.DateTimeField(auto_now=True)
    is_success = models.BooleanField()
class Instance(models.Model):
    name = models.CharField(max_length=30)
    available = models.BooleanField(default=True)
