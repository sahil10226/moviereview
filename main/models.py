from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Movie(models.Model):
    name = models.CharField(max_length=400)
    director = models.CharField(max_length=400)
    cast = models.CharField(max_length=900)
    description = models.TextField(max_length=5000)
    release_date = models.DateField(null=True, blank=True)
    averageRating = models.FloatField(default=0)
    image = models.URLField(default=None, null=True)

    def __str__(self):
        return self.name
    
    def __unicode__(self):
        return self.name
    
class Review(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    comment = models.TextField(max_length=1000)
    rating = models.FloatField(default=0)

    def __str__(self):
        return self.user.username