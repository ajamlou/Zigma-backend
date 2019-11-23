from rest_framework import routers
from django.urls import path, include
from book import views

router = routers.DefaultRouter()
router.register('books', views.BookViewSet, basename='book')

urlpatterns = [
    path('', include(router.urls)),
]
