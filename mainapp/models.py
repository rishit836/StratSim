from django.db import models
from django.contrib.auth.models import User
from collections import deque
from django.dispatch import receiver
from django.db.models.signals import post_save

# from django.contrib.postgres.fields import JSONField

# Create your models here.
class growth(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    fund_history = models.JSONField(default=list)
    
    def push(self,fund,max_length:int=10):
        if len(self.fund_history) > max_length:
            self.fund_history.pop(0) # removing the oldest entry (FIFO:First in First Out)
        self.fund_history.append(fund)
        self.save()

@receiver(post_save,sender=User)
def model_create_growth(sender,instance,created,**kwargs):
    if created:
        growth.objects.create(user=instance)