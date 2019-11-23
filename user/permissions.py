from rest_framework import permissions
from django.contrib.auth.models import User

class IsOwner(permissions.BasePermission):

    def has_permission(self, request, view):
        # can write custom code
        try:
            user = User.objects.get(
                pk=view.kwargs['pk'])
        except:
            return False

        return request.user == user
