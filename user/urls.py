from . import views
from django.urls import path, include
from rest_framework import routers

# user_list = views.UserViewSet.as_view({'get': 'list'})
# user_detail = views.UserViewSet.as_view({'get': 'retrieve','patch': 'partial_update', 'delete':'destroy' })
# user_create = views.UserViewSet.as_view({'post': 'create'})
router = routers.SimpleRouter()
router.register('users', views.UserViewSet, basename='user')
obtain_auth_token = views.CustomObtainAuthToken.as_view()

urlpatterns = [
    # path('create-user/', user_create, name='account-create'),
    # path('list-users/', user_list, name='list-users'),
    # path('user/<int:pk>/', user_detail, name='user'),
    path('', include(router.urls)),
    path('login/', obtain_auth_token, name='api-token-auth'),
    path('profile_pic/<int:pk>/', views.RetrieveProfileView.as_view(), name='profile'),
    path('test/<int:pk>/', views.test.as_view(), name='profile')
]
