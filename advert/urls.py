from rest_framework import routers
from django.urls import path, include
from advert import views

#advert_detail = views.AdvertViewSet.as_view({'get': 'retrieve','patch': 'partial_update', 'delete':'destroy', 'post':'create', })
router = routers.DefaultRouter()
router.register('adverts', views.AdvertViewSet, basename='advert')
#router.register('advertimages', views.AdvertImageViewSet, basename='advertimage')

urlpatterns = [
    path('', include(router.urls)),
    path('advertimages/<int:pk>/', views.RetrieveAdvertImageView.as_view(), name='image')
    #path('adverts/<int:pk>/', advert_detail, name='adverts'),
]
