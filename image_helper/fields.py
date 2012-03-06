
import os
from cStringIO import StringIO
import mimetypes

from django.db.models.fields.files import ImageField
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.models import signals

from PIL import Image

# todo: Add 'delete_with_model' option that will delete thumbnail and image when model is deleted.

class ThumbnailField(object):
    """
    Instances of this class will be used to access data of the
    generated thumbnails
    """

    def __init__(self, name, storage):
        """
        Uses same storage as the parent field
        """
        self.name = name
        self.storage = storage

    def path(self):
        return self.storage.path(self.name)

    def url(self):
        return self.storage.url(self.name)

    def size(self):
        return self.storage.size(self.name)


class SizedImageField(ImageField):
    """
    An Image field that allows auto resizing auto creation of thumbnails.
    """

    def __init__(self, verbose_name=None, name=None, width_field=None,
                       height_field=None, size=None, thumbnail_size=None, **kwargs):
        """
        Added fields:
            - size: a tuple containing width and height to resize image, and
                an optional boolean setting if is wanted forcing that size
                (None for not resizing).
            - thumbnail_size: a tuple with same values than `size' (None for
                not creating a thumbnail

        Example: (640, 480, True) -> Will resize image to a width of 640px and
            a height of 480px. File will be cut if necessary for forcing
            the image to have the desired size
        """
        self.size = self._get_resize_options(size)
        self.thumbnail_size = self._get_resize_options(thumbnail_size)

        super(SizedImageField, self).__init__(verbose_name, name, width_field, height_field, **kwargs)

    def _get_resize_options(self, dimensions):
        """
        :param dimensions:
            A tuple of (width, height, force_size).
            'force_size' can be left off and will default to False.
        """
        if dimensions and isinstance(dimensions, (tuple, list)):
            if len(dimensions) < 3:
                dimensions = tuple(dimensions) + (False,)
            return dimensions

    def contribute_to_class(self, cls, name):
        """
        Makes sure thumbnail gets set when image field initialized.
        """
        super(SizedImageField, self).contribute_to_class(cls, name)
        signals.post_init.connect(self._set_thumbnail, sender=cls)

    def pre_save(self, model_instance, add):
        """
        Resizes, commits image to storage, and returns field's value just before saving.
        """
        file = getattr(model_instance, self.attname)
        if file and not file._committed:
            file.file = self._resize_image(model_instance, file)
            file.save(file.name, file, save=False)
        return file

    def _get_thumbnail_filename(self, filename):
        """
        Returns a thumbnail version of the file name.
        """
        name, ext = os.path.splitext(filename)
        return ''.join([name, '-thumbnail', ext])

    def _create_thumbnail(self, model_instance, thumbnail, image_name):
        """
        Because of how we are using the base file name as a reference to the
        thumbnail and not storing it off anywhere, we need to make sure to
        run the name through the storage's `get_available_name` so the name
        doesn't change once we actually save it.
        """
        thumbnail = self._do_resize(thumbnail, self.thumbnail_size)

        full_image_name = self.storage.get_available_name(self.generate_filename(model_instance, image_name))
        thumbnail_filename = self._get_thumbnail_filename(full_image_name)
        thumb = self._get_simple_uploaded_file(thumbnail, thumbnail_filename)
        self.storage.save(thumbnail_filename, thumb)

    def _resize_image(self, model_instance, image_field):
        """"""
        image_name = image_field.name

        image = Image.open(image_field.file)
        if image.mode not in ('L', 'RGB'):
            image = image.convert('RGB')

        if self.size:
            image = self._do_resize(image, self.size)

        if self.thumbnail_size:
            self._create_thumbnail(model_instance, image.copy(), image_name)

        return self._get_simple_uploaded_file(image, image_name)

    def _do_resize(self, img, dimensions):
        width, height, force_size = dimensions
        if force_size:
            img.resize((width, height), Image.ANTIALIAS)
        else:
            img.thumbnail((width, height), Image.ANTIALIAS)
        return img

    def _set_thumbnail(self, instance=None, **kwargs):
        """
        Sets a `thumbnail` attribute on the image field class.
        On thumbnail you can access name, url, path attributes
        """
        image_field = getattr(instance, self.name)
        if image_field:
            filename = self.generate_filename(instance, image_field.name)
            thumbnail_filename = self._get_thumbnail_filename(filename)

            thumbnail_field = ThumbnailField(thumbnail_filename, self.storage)
            setattr(image_field, 'thumbnail', thumbnail_field)

    def _get_simple_uploaded_file(self, image, file_name):
        """
        :param image:
            a python PIL ``Image`` instance.

        :param file_name:
            The file name of the image.

        :returns:
            A django ``SimpleUploadedFile`` instance ready to be saved.
        """
        extension = os.path.splitext(file_name)[1]

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


try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], ["^image_helper\.fields\.SizedImageField"])
except ImportError:
    pass
