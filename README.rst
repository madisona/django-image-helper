Django Image Helper
===================

Provides a model mixin that has 'image' and 'thumbnail' fields.
The uploaded image will be scaled to the model's 'IMAGE_SIZE' and
a thumbnail will be scaled and saved to the model's 'THUMBNAIL_SIZE'.

Additionally, there is an admin mixin to help you display an image's thumbnail
when in the admin's listview.

RELEASE NOTES:

  **version 0.1.1**
  Added AdminImagePreviewWidget. This will show a preview of the image in the
  admin change_form view in addition to the link the admin already shows.

  To enable, add the following to your ModelAdmin.

    .. code:: python

      formfield_overrides = {
          SizedImageField: {'widget': AdminImagePreviewWidget},
      }

  **version 0.1.0**
  Added SizedImageField. This lets you do the same thing the ``ImageMixin``
  was used for, but isolates all the work to the model's field. It should
  work with any storage backend.

  See the example project for a working sample. The basics:

  class MyModel(models.Model):
    image = fields.SizedImageField(upload_to="the_directory", size=(500, 500), thumbnail_size=(200, 200))


  Then you can access both the image and thumbnail in code or templates by:
    model.image.url
    model.image.thumbnail.url


