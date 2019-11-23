"""zigma_backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path,include
from rest_framework.authtoken import views
from django.conf.urls.static import static
from . import settings
from rest_framework_swagger.views import get_swagger_view

schema_view = get_swagger_view(title='Dokumentation över API:er')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', schema_view),

    #path('api/', include('api.urls')),

    path('users/', include('user.urls')),
    path('adverts/', include('advert.urls')),
    path('books/', include('book.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += [path('silk/', include('silk.urls', namespace='silk'))]
