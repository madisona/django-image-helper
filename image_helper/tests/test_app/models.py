from django.db import models
from image_helper.fields import SizedImageField


class TestModel(models.Model):
    image = SizedImageField(upload_to='test_images', size=(220, 150), thumbnail_size=(100, 100))
