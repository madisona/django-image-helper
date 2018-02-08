from django.contrib import admin

from image_helper.fields import SizedImageField
from image_helper.widgets import AdminImagePreviewWidget

from sample.models import TestModel


class TestModelAdmin(admin.ModelAdmin):
    list_display = ['preview_thumbnail', 'name']

    def preview_thumbnail(self, obj):
        return '<img src="{}" />'.format(obj.image.thumbnail.url)

    preview_thumbnail.allow_tags = True

    formfield_overrides = {
        SizedImageField: {
            'widget': AdminImagePreviewWidget
        },
    }


admin.site.register(TestModel, TestModelAdmin)
