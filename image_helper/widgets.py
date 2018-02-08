from django.contrib.admin.widgets import AdminFileWidget
from django.utils.safestring import mark_safe


class AdminImagePreviewWidget(AdminFileWidget):
    """
    An admin widget that shows a preview of currently selected image.
    """

    def __init__(self, attrs=None, storage=None):
        super(AdminImagePreviewWidget, self).__init__(attrs)

    def render(self, name, value, attrs=None):
        content = super(AdminImagePreviewWidget, self).render(name, value, attrs)
        return mark_safe(content + self._get_preview_tag(value))

    def _get_preview_tag(self, value):
        if value and hasattr(value, "url"):
            return '<p class="file-upload current-file-preview">Current Preview:<br />' \
                   '<img src="{0}" style="max-width: 300px;" /></p>'.format(value.url)
        return ''
