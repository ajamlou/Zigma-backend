from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from django.http.response import StreamingHttpResponse
from rest_framework import status, generics, viewsets
from user.serializers import UserCreateSerializer, UserSerializer,ImageSerializer# UserUpdateSerializer
from django.contrib.auth.models import User
from .models import UserProfile
from advert.models import Advert
from django.db.models import Prefetch
from rest_framework.permissions import AllowAny, IsAuthenticated
from .permissions import IsOwner
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken, APIView
import json
import mimetypes
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter

class CustomObtainAuthToken(ObtainAuthToken):
    """
    POST users/login/:
    Denna endpoint verifierar inloggningsuppgifter och returnerar token, id, email, username, image och adverts
    """
    def post(self, request, *args, **kwargs):
        response = super(self.__class__, self).post(request, *args, **kwargs)

        token_queryset = Token.objects.filter(key=response.data['token'])\
        .select_related('user')\
        .select_related('user__profile_picture')

        token, isCreated = token_queryset.get_or_create(key=response.data['token'])

        try:
            profile = token.user.profile_picture.pk
        except:
            profile = None
        email = token.user.email
        username = token.user.username
        adverts = token.user.adverts.values_list('id', flat=True)
        return Response({
        'token': token.key,
        'id': token.user.id,
        'email': email,
        'username':username,
        'profile':profile,
        'has_picture':bool(token.user.profile_picture.image),
        'adverts': adverts})


class UserViewSet(viewsets.ModelViewSet):
    """
    GET users/users/:
    Returnerar alla users.

    GET users/users/1/:
    Returnerar user med ID:t '1'

    POST users/users/:
    Skapar en ny user

    PATCH users/users/1/:
    Uppdaterar user-information

    DELETE users/users/1/:
    Raderar en user från databasen

    """
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)
    ordering_fields = ('username',)
    search_fields = ('id','username','email','profile_picture','image',)

    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_queryset(self):
        queryset = self.get_serializer_class()\
        .setup_eager_loading(self.queryset,'profile_picture', 'adverts', 'accepted_adverts')
        return queryset

    def get_object(self):
        if self.action in ('update','partial_update','destroy'):
            return get_object_or_404(self.get_queryset(), pk=self.request.user.id)
        elif self.action in ('retrieve'):
            return get_object_or_404(self.get_queryset(), pk=self.kwargs['pk'])
        else:
            return super(self.__class__,self).get_object()

    def get_permissions(self):
       if self.action in ('update','partial_update','destroy'):
           self.permission_classes = (IsAuthenticated, IsOwner,)
       if self.action in ('list','retrieve','create'):
           self.permission_classes = (AllowAny,)
       return super(self.__class__, self).get_permissions()

    def get_serializer_class(self):
        if self.action in ('create'):
            return UserCreateSerializer
        return super(self.__class__, self).get_serializer_class()

    #get_serializer(self, instance=None, data=None, many=False, partial=False):




    # def list(self, request):
    #     serializer = UserSerializer(self.get_queryset(), many=True, context={'request':request})
    #     return Response(serializer.data)

    def retrieve(self, request, pk=None):
        user = self.get_object()
        serializer = self.get_serializer(user, context={'request': request})
        return Response(serializer.data)

    def list(self, request):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(serializer.data)

    def create(self, request, format='json'):
        serializer = UserCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.save()
            if user:
                token = Token.objects.create(user=user)
                jsonResponse = serializer.data
                jsonResponse['token'] = token.key
                return Response(jsonResponse, status=status.HTTP_201_CREATED)

        #Om vi får felmeddelanden vill frontend inte ha dessa som listor utan i strängar
        jsonErrors = serializer.errors
        try:
            old_data = jsonErrors.pop('username')
            jsonErrors["username"] = "This username is either invalid or already in use"
        except:
            pass
        try:
            old_data = jsonErrors.pop('email')
            jsonErrors['email'] = "This email is either invalid or already in use"
        except:
            pass
        try:
            old_data = jsonErrors.pop('password')
            jsonErrors['password'] = "Password has to be at least 8 characters"
        except:
            pass

        return Response(jsonErrors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, *args, **kwargs):
        user = self.get_object()
        userSerializer = UserSerializer(user,
        data=request.data,
        partial=True,
        context={'request': request})
        userSerializer.is_valid(raise_exception=True)
        userSerializer.save()
        response_dict = dict()
        for key, value in request.data.items():
            if key == 'password':
                pass
            elif key == 'profile_picture':
                pass
                #response_dict['img_link'] = userSerializer.data['img_link']
            else:
                response_dict[key] = userSerializer.data[key]
        return Response(response_dict, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class RetrieveProfileView(generics.RetrieveAPIView):
    permission_classes = (AllowAny,)

    def get_queryset(self):
        return UserProfile.objects.filter(pk=self.kwargs['pk'])

    def get_object(self):
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, pk=self.kwargs['pk'])
        return obj

    def retrieve(self,request, *args, **kwargs):
        image_obj = self.get_object()
        filename = image_obj.image

        if not filename:
            return Response(status=status.HTTP_404_NOT_FOUND)

        size = filename.size
        path = filename.path
        content_type_file = mimetypes.guess_type(path)[0]
        response = StreamingHttpResponse(open(path, 'rb'), content_type=content_type_file)
        response['Content-Disposition'] = "attachment; filename=%s" % str(filename)
        response['Content-Length'] = size
        return response

class test(generics.RetrieveAPIView):
    permission_classes = (AllowAny,)


    def retrieve(self, request, *args, **kwargs):
        return Response(status=status.HTTP_200_OK)
