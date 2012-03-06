
from django.conf import settings
from django.conf.urls.defaults import patterns, include, url

from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'example.views.home', name='home'),
    # url(r'^example/', include('example.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)




# serve media files for sample stuff to work.
if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^%s(?P<path>.*)$' % settings.MEDIA_URL.lstrip('/'), 'django.views.static.serve', kwargs={
            'document_root': settings.MEDIA_ROOT,
        }),
    )
