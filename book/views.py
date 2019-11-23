from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status, generics
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import Book
from .serializers import BookSerializer

class BookViewSet(viewsets.ModelViewSet):

    serializer_class = BookSerializer
    queryset = Book.objects.all()
    permission_classes = (AllowAny,)

    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)
    # filter_fields = ('transaction_type','state','owner','id',)
    ordering_fields = ('book_title','authors','edition','created_at')
    search_fields = ('book_title','authors','ISBN','edition')

    def get_permissions(self):
       if self.action in ('create',):
           self.permission_classes = (IsAuthenticated,)
       if self.action in ('destroy', 'partial_update', 'update'):
           self.permission_classes = (IsAuthenticated,)
       if self.action in ('list','retrieve'):
           self.permission_classes = (AllowAny,)
       return super(self.__class__, self).get_permissions()
