from django.db import models

from image_helper.fields import SizedImageField


# Create your models here.
class TestModel(models.Model):
    name = models.CharField(max_length=20)
    image = SizedImageField(upload_to='sample_images', size=(220, 150), thumbnail_size=(100, 100))
