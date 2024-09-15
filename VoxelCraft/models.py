
from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    image = models.ImageField(upload_to='products/')
    image_modalidad = models.ImageField(upload_to='products/modalidad')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    category = models.CharField(max_length=100)
    modality = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
class ServerInfo(models.Model):
    image = models.ImageField(upload_to='new-servers/')
    ip_address = models.CharField(max_length=255)
    port = models.IntegerField()

    def __str__(self):
        return f"{self.ip_address}:{self.port}"