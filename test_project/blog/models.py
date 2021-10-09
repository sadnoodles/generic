from django.db import models
from gras.models import CommonAttr

# Create your models here.

class Blog(CommonAttr):
    title = models.CharField(max_length=200, blank=True)
    content = models.TextField()

class Comment(CommonAttr):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)
    content = models.TextField()