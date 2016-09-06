"""
Definition of urls for SquareWorld.
"""

from django.conf.urls import include, url
from django.conf.urls.static import static
from SquareWorld import settings

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = [
    # Examples:
    # url(r'^$', 'SquareWorld.views.home', name='home'),
    # url(r'^SquareWorld/', include('SquareWorld.SquareWorld.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    url(r'^SquareVeg/', include('SquareVeg.urls')),
    url('', include('social.apps.django_app.urls', namespace='social')),
    url('', include('django.contrib.auth.urls', namespace='auth')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

