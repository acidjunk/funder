from django.conf.urls import include, url, patterns
from django.conf import settings
from django.contrib import admin

from wagtail.wagtailadmin import urls as wagtailadmin_urls
from wagtail.wagtaildocs import urls as wagtaildocs_urls
from wagtail.wagtailcore import urls as wagtail_urls

from search.views import search
from fundraiser.views import project_search, product_search


urlpatterns = [
    url(r'^blog/', include('blog.urls', namespace="blog")),
    url(r'^projects/', include('fundraiser.urls', namespace="project")),
    url(r'^products/', include('fundraiser.urls', namespace="product")),
    url(r'^orders/', include('fundraiser.urls', namespace="order")),
    url(r'^django-admin/', include(admin.site.urls)),
    url(r'^admin/', include(wagtailadmin_urls)),
    url(r'^documents/', include(wagtaildocs_urls)),
    url(r'^search/$', search, name='search'),
    url(r'^projects/search/$', project_search, name='project_search'),
    url(r'^products/search/$', product_search, name='product_search'),
    url(r'', include(wagtail_urls)),
]

if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    from django.views.generic import TemplateView

    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
