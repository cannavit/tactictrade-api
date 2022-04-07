from django.db import models

class symbol(models.Model):

    symbolName = models.CharField(blank=False, null=False,max_length=10)
    image = models.ImageField(upload_to='avatars/', null=True, blank=True)

def __str__(self):
    return self.symbolName