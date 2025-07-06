from django.db import models
from django.contrib.auth.models import User
from collections import deque
# from django.contrib.postgres.fields import JSONField

# Create your models here.
class growth(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)