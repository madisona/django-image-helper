import os
import shutil
from os.path import join, dirname

from django import test
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.conf import settings

from image_helper.tests.test_app.models import TestModel
from image_helper.fields import _get_thumbnail_filename


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

    def _save_image_model(self):
        upload_file = self._get_simple_uploaded_file()
        m = TestModel(image=upload_file)
        m.save()
        return m

    def test_saves_image_and_thumbnail(self):
        upload_file = self._get_simple_uploaded_file()
        m = TestModel(image=upload_file)
        m.save()

        model = TestModel.objects.get(pk=1)
        self.assertEqual("test_images/sample_photo.png", model.image.name)
        self.assertEqual("{}test_images/sample_photo.png".format(settings.MEDIA_URL), model.image.url)
        self.assertEqual("{}/test_images/sample_photo.png".format(settings.MEDIA_ROOT), model.image.path)
        self.assertEqual(True, os.path.exists(model.image.path))

        self.assertEqual("test_images/sample_photo-thumbnail.png", model.image.thumbnail.name)
        self.assertEqual(
            "{}test_images/sample_photo-thumbnail.png".format(settings.MEDIA_URL), model.image.thumbnail.url
        )
        self.assertEqual(
            "{}/test_images/sample_photo-thumbnail.png".format(settings.MEDIA_ROOT), model.image.thumbnail.path
        )
        self.assertEqual(True, os.path.exists(model.image.thumbnail.path))

    def test_saves_appropriately_when_finding_valid_image_name(self):
        # Thumbnail should be named the same as image, just with the -thumbnail piece.
        self._save_image_model()
        self._save_image_model()

        model = TestModel.objects.get(pk=2)
        self.assertTrue(model.image.name.startswith("test_images/sample_photo"))
        self.assertNotEqual("test_images/sample_photo.png", model.image.name)
        self.assertEqual("{}{}".format(settings.MEDIA_URL, model.image.name), model.image.url)
        self.assertEqual("{}/{}".format(settings.MEDIA_ROOT, model.image.name), model.image.path)
        self.assertEqual(True, os.path.exists(model.image.path))

        expected_thumbnail_name = _get_thumbnail_filename(model.image.name)
        self.assertEqual(expected_thumbnail_name, model.image.thumbnail.name)
        self.assertEqual("{}{}".format(settings.MEDIA_URL, expected_thumbnail_name), model.image.thumbnail.url)
        self.assertEqual("{}/{}".format(settings.MEDIA_ROOT, expected_thumbnail_name), model.image.thumbnail.path)
        self.assertEqual(True, os.path.exists(model.image.thumbnail.path))


class GetThumbnailFilenameTests(test.TestCase):
    def test_get_thumbnail_filename(self):
        thumbnail_name = _get_thumbnail_filename("my_image.jpg")
        self.assertEqual("my_image-thumbnail.jpg", thumbnail_name)

    def test_allows_customized_append_text(self):
        thumbnail_name = _get_thumbnail_filename("my_image.jpg", append_text="-small")
        self.assertEqual("my_image-small.jpg", thumbnail_name)
