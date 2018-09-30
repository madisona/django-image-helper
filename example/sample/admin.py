from django.contrib import admin
from django.utils.safestring import mark_safe

from image_helper.fields import SizedImageField
from image_helper.widgets import AdminImagePreviewWidget

from sample.models import TestModel


class TestModelAdmin(admin.ModelAdmin):
    list_display = ['preview_thumbnail', 'name']

    def preview_thumbnail(self, obj):
        return mark_safe('<img src="{}" />'.format(obj.image.thumbnail.url))

    formfield_overrides = {
        SizedImageField: {
            'widget': AdminImagePreviewWidget
        },
    }


admin.site.register(TestModel, TestModelAdmin)
