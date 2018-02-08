import os
import shutil
from os.path import join, dirname

from django import test
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.conf import settings

from image_helper.tests.test_app.models import TestModel


@test.override_settings(INSTALLED_APPS=['image_helper.tests.test_app'])
class SizedImageFieldTests(test.TestCase):

    def setUp(self):
        call_command("migrate", verbosity=0)

    def tearDown(self):
        shutil.rmtree(os.path.join(settings.MEDIA_ROOT, "test_images"))

    def test_saves_image(self):
        upload_file = SimpleUploadedFile(
            "sample_photo.png",
            open(join(dirname(__file__), "test_app/sample_photo.png"), 'rb').read(),
            content_type="image/png"
        )
        m = TestModel(image=upload_file)
        m.save()

        model = TestModel.objects.get(pk=1)
        self.assertEqual("test_images/sample_photo.png", model.image.name)
        self.assertEqual("{}test_images/sample_photo.png".format(settings.MEDIA_URL), model.image.url)
        self.assertEqual("{}/test_images/sample_photo.png".format(settings.MEDIA_ROOT), model.image.path)
        self.assertEqual(25822, model.image.size)

    def test_saves_thumbnail(self):
        upload_file = SimpleUploadedFile(
            "sample_photo.png",
            open(join(dirname(__file__), "test_app/sample_photo.png"), 'rb').read(),
            content_type="image/png"
        )
        m = TestModel(image=upload_file)
        m.save()

        model = TestModel.objects.get(pk=1)
        self.assertEqual("test_images/sample_photo-thumbnail.png", model.image.thumbnail.name)
        self.assertEqual(
            "{}test_images/sample_photo-thumbnail.png".format(settings.MEDIA_URL), model.image.thumbnail.url
        )
        self.assertEqual(
            "{}/test_images/sample_photo-thumbnail.png".format(settings.MEDIA_ROOT), model.image.thumbnail.path
        )
        self.assertEqual(6764, model.image.thumbnail.size)
