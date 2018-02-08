import os

from io import BytesIO

import mimetypes

from django.db.models.fields.files import ImageField
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.models import signals

from PIL import Image

# todo: Add 'delete_with_model' option that will delete thumbnail and image when model is deleted.


def _get_thumbnail_filename(filename, append_text="-thumbnail"):
    """
    Returns a thumbnail version of the file name.
    """
    name, ext = os.path.splitext(filename)
    return ''.join([name, append_text, ext])


class ThumbnailField(object):
    """
    Instances of this class will be used to access data of the
    generated thumbnails. A thumbnail is created when the image is saved
    initially, but there's nothing persisted that references the thumbnail.
    When the `SizedImageField` is instantiated, it gets this thumbnail
    field attached to it where the thumbnail becomes accessible.

    for example: `image.thumbnail.url`
    """

    def __init__(self, name, storage):
        """
        Uses same storage as the parent field
        """
        self.name = name
        self.storage = storage

    @property
    def path(self):
        return self.storage.path(self.name)

    @property
    def url(self):
        return self.storage.url(self.name)

    @property
    def size(self):
        return self.storage.size(self.name)


class SizedImageField(ImageField):
    """
    An Image field that allows auto resizing auto creation of thumbnails.
    """

    def __init__(
        self,
        verbose_name=None,
        name=None,
        width_field=None,
        height_field=None,
        size=None,
        thumbnail_size=None,
        **kwargs
    ):
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
                dimensions = tuple(dimensions) + (False, )
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
            file.name = self._clean_file_name(model_instance, file.name)
            file.file = self._resize_image(model_instance, file)
            file.save(file.name, file, save=False)
        return file

    def _clean_file_name(self, model_instance, filename):
        """
        We need to make sure we know the full file name before we save the thumbnail so
        we can be sure the name doesn't change on save.

        This method gets the available filename and returns just the file part.
        """
        available_name = self.storage.get_available_name(self.generate_filename(model_instance, filename))
        return os.path.basename(available_name)

    def _create_thumbnail(self, model_instance, thumbnail, image_name):
        """
        Resizes and saves the thumbnail image
        """
        thumbnail = self._do_resize(thumbnail, self.thumbnail_size)
        full_image_name = self.generate_filename(model_instance, image_name)
        thumbnail_filename = _get_thumbnail_filename(full_image_name)
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
            thumbnail_filename = _get_thumbnail_filename(image_field.name)

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

        temp_handle = BytesIO()
        image.save(temp_handle, self._get_pil_format(extension))
        temp_handle.seek(0)  # rewind the file

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
