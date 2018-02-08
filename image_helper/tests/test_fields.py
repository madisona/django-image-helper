import os
import shutil
from os.path import join, dirname

from django import test
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.conf import settings

from image_helper.tests.test_app.models import TestModel
from image_helper.fields import SizedImageField


class SizedImageFieldTests(test.TestCase):

    def setUp(self):
        call_command("migrate", verbosity=0)

    def tearDown(self):
        test_images_path = os.path.join(settings.MEDIA_ROOT, "test_images")
        if os.path.exists(test_images_path):
            shutil.rmtree(test_images_path)

    def _get_simple_uploaded_file(self):
        return SimpleUploadedFile(
            "sample_photo.png",
            open(join(dirname(__file__), "test_app/sample_photo.png"), 'rb').read(),
            content_type="image/png"
        )

    def test_saves_image_and_thumbnail(self):
        upload_file = self._get_simple_uploaded_file()
        m = TestModel(image=upload_file)
        m.save()

        model = TestModel.objects.get(pk=1)
        self.assertEqual("test_images/sample_photo.png", model.image.name)
        self.assertEqual("{}test_images/sample_photo.png".format(settings.MEDIA_URL), model.image.url)
        self.assertEqual("{}/test_images/sample_photo.png".format(settings.MEDIA_ROOT), model.image.path)

        self.assertEqual("test_images/sample_photo-thumbnail.png", model.image.thumbnail.name)
        self.assertEqual(
            "{}test_images/sample_photo-thumbnail.png".format(settings.MEDIA_URL), model.image.thumbnail.url
        )
        self.assertEqual(
            "{}/test_images/sample_photo-thumbnail.png".format(settings.MEDIA_ROOT), model.image.thumbnail.path
        )

    def test_get_thumbnail_filename(self):
        f = SizedImageField()
        thumbnail_name = f._get_thumbnail_filename("my_image.jpg")
        self.assertEqual("my_image-thumbnail.jpg", thumbnail_name)
