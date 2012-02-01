
from cStringIO import StringIO
import mimetypes
import os

from PIL import Image

from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import models

class ImageMixin(models.Model):
    """
    Provides a model class with a `image` and `thumbnail` fields.
    You can customize the size of the images by changing the
    IMAGE_SIZE and THUMBNAIL_SIZE properties on the destination model.
    """
    IMAGE_SIZE = (540, 900)
    THUMBNAIL_SIZE = (180, 300)

    image = models.ImageField(
        upload_to='images',
        width_field='image_width',
        height_field='image_height',
        )
    image_url = models.URLField(editable=False)
    image_width = models.IntegerField(auto_created=True)
    image_height = models.IntegerField(auto_created=True)

    thumbnail = models.ImageField(
        upload_to='thumbnails',
        width_field='thumbnail_width',
        height_field='thumbnail_height',
        )
    thumbnail_url = models.URLField(editable=False)
    thumbnail_width = models.IntegerField(auto_created=True)
    thumbnail_height = models.IntegerField(auto_created=True)

    def _resize_images(self):
        """
        Resizes images to have the sizes defined by:
          IMAGE_SIZE
          THUMBNAIL_SIZE
        """
        name, extension = os.path.splitext(self.image.name)
        image = Image.open(self.image)
        if image.mode not in ('L', 'RGB'):
            image = image.convert('RGB')
        thumbnail = image.copy()

        # resize images maintaining aspect ratios
        image.thumbnail(self.IMAGE_SIZE, Image.ANTIALIAS)
        thumbnail.thumbnail(self.THUMBNAIL_SIZE, Image.ANTIALIAS)

        # put resized images on model
        self.image = self._get_simple_uploaded_file(image, name, extension)
        self.thumbnail = self._get_simple_uploaded_file(thumbnail, name, extension)

    def _get_simple_uploaded_file(self, image, name, extension):
        """
        :param image:
            a python PIL ``Image`` instance.

        :param name:
            The file name without the extension.

        :param extension:
            The file extension.

        :returns:
            A django ``SimpleUploadedFile`` instance ready to be saved.
        """
        file_name = name + extension
        mimetype, encoding = mimetypes.guess_type(file_name)
        content_type = mimetype or 'image/png'

        temp_handle = StringIO()
        image.save(temp_handle, self._get_pil_format(extension))
        temp_handle.seek(0) # rewind the file

        suf = SimpleUploadedFile(
            file_name,
            temp_handle.read(),
            content_type=content_type,
            )
        return suf

    def _get_pil_format(self, extension):
        """
        :param extension:
            The file name extension (.png, .jpg, etc...)

        :returns:
            The file format PIL needs from the file extension.
            Eg. PNG or JPEG
        """
        return Image.EXTENSION[extension.lower()]

    def delete(self, using=None):
        """
        When deleting the model, make sure to delete the images
        so they're not orphaned in their storage facility.
        """
        self.image.delete(save=False)
        self.thumbnail.delete(save=False)
        super(ImageMixin, self).delete(using=using)

    def save(self, *args, **kwargs):
        """
        Resize the Images, save the model, then update the image urls
        so they don't need to be re-calculated every time they're used.
        """
        if self.image and not self.image._committed:
            self._resize_images()
        super(ImageMixin, self).save(*args, **kwargs)

    class Meta(object):
        abstract = True
