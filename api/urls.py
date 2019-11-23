from rest_framework import routers
from django.urls import path, include
from api import views

router = routers.DefaultRouter()
router.register('users', views.UserViewSet)
router.register('books', views.BookViewSet)
router.register('authors', views.AuthorViewSet)
router.register('adverts', views.AdvertViewSet, basename='advert')
router.register('advertimages', views.AdvertImageViewSet, basename='advertimage')

urlpatterns = [
    path('', include(router.urls))
]
