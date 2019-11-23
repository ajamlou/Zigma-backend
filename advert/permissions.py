from rest_framework import permissions
from django.contrib.auth.models import User
from .models import Advert


class IsOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        try:
            advert = Advert.objects.get(
                pk=view.kwargs['pk'])
        except:
            return False
        return request.user == advert.owner
