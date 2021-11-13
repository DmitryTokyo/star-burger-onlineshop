from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include, re_path
from django.shortcuts import render
from django.conf import settings


urlpatterns = [
    re_path(r'^admin/', admin.site.urls),
    path('', render, kwargs={'template_name': 'index.html'}, name='start_page'),
    path('api/', include('foodcartapp.urls')),
    path('manager/', include('restaurateur.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
