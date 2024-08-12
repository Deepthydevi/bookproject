# Create your models here.
from django.db import models


class Books(models.Model):
    title = models.CharField(max_length=100)
    author = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='book_media')
    quantity = models.IntegerField()


    def __str__(self):
        return '{}'.format(self.title)
