from django.db import models


# Create your models here.
class InputMessage(models.Model):
    when = models.DateTimeField("date created", auto_now_add=True)
    who = models.TextField("who created")
    request_body = models.TextField('request body', null=True)
