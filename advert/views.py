from advert.models import Advert, AdvertImage
from django.shortcuts import get_object_or_404
from advert.serializers import AdvertSerializer, AdvertImageSerializer, AdvertPostSerializer, AdvertRetrieveSerializer
from rest_framework import viewsets, status, generics
from rest_framework.response import Response
from django.http.response import StreamingHttpResponse
from rest_framework.decorators import action
from .permissions import IsOwner
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth.models import User
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
import mimetypes

class AdvertViewSet(viewsets.ModelViewSet):
    """
    En ModelViewSet är en grupp av views bestående av:
    list, create, retrieve, update, partially_update, destroy
    """
    queryset = Advert.objects.all()
    permission_classes = (AllowAny,)

    # Implementerar Django filters
    # Ex. på URL: /adverts/adverts/?fields=price,book_title,authors,
    #              edition&ordering=-price  <- visar de specifika fälten och
    # sorterar på fallande pris
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)
    filter_fields = ('transaction_type','state','owner','id',)
    ordering_fields = ('book_title','authors','price','edition','created_at')
    search_fields = ('book_title','authors','ISBN',)

    def get_queryset(self):
        #queryset = super(AdvertViewSet, self).get_queryset()
        if self.action not in ('create'):
            queryset = self.get_serializer_class().setup_eager_loading(super(AdvertViewSet, self).get_queryset())
        else:
            queryset = super(AdvertViewSet, self).get_queryset()

        ids = self.request.query_params.get('ids', None)
        if ids is not None:
            ids_list = ids.split(',')

            #Ger 0 träffar om param 'ids' finns men inget anges
            if len(ids_list) == 1 and ids_list[0] == '':
                return Advert.objects.none()

            queryset = queryset.filter(id__in=ids_list).order_by('-created_at')

        return queryset

    def get_serializer_class(self):
        if self.action in ('create', 'partial_update'):
            return AdvertPostSerializer
        if self.action in ('retrieve',):
            return AdvertRetrieveSerializer
        return AdvertSerializer

    def get_permissions(self):
       if self.action in ('create',):
           self.permission_classes = (IsAuthenticated,)
       if self.action in ('destroy', 'partial_update', 'update'):
           self.permission_classes = (IsAuthenticated, IsOwner,)
       if self.action in ('list','retrieve'):
           self.permission_classes = (AllowAny,)
       return super(self.__class__, self).get_permissions()

    def get_object(self):
        if self.action in('partial_update'):
            return get_object_or_404(self.get_queryset(),pk=self.kwargs['pk'])
        else:
            return super(self.__class__, self).get_object()

    def perform_create(self, serializer):
        return serializer.save(owner=self.request.user)

    @action(detail=False, methods=['get'])
    def recent_adverts(self, request):
        recent_adverts = self.get_queryset().order_by('-created_at')[:20]
        serializer = self.get_serializer(recent_adverts, many=True)
        return Response(serializer.data)

    def partial_update(self, request, *args, **kwargs):
        advert = self.get_object()
        data = request.data.copy()
        if 'owner' in data:
            del data['owner']

        advertSerializer = AdvertSerializer(advert,
        data=data,
        partial=True,
        context={'request': request})
        advertSerializer.is_valid(raise_exception=True)
        advertSerializer.save()
        return Response(advertSerializer.data)

    def list(self, request):
        return super(self.__class__,self).list(self, request)


class RetrieveAdvertImageView(generics.RetrieveAPIView):
    serializer_class = AdvertImageSerializer
    queryset = AdvertImage.objects.all()
    permission_classes = (AllowAny,)


    def retrieve(self,request, *args, **kwargs):
        image_obj = self.get_object()
        filename = image_obj.image
        size = filename.size
        content_type_file = mimetypes.guess_type(filename.path)[0]
        response = StreamingHttpResponse(open(image_obj.image.path, 'rb'), content_type=content_type_file)
        response['Content-Disposition'] = "attachment; filename=%s" % str(filename)
        response['Content-Length'] = size
        return response
