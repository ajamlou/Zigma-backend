from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth.models import User
from advert.models import Advert
from .models import UserProfile
from drf_extra_fields.fields import Base64ImageField
from drf_queryfields import QueryFieldsMixin
from django.db.models import Prefetch

class PKField(serializers.RelatedField):
    def to_representation(self,instance):
        return instance.pk

class UserCreateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
    required=True,
    validators=[UniqueValidator(queryset=User.objects.all(), message='This email is already taken')]
    )

    username = serializers.CharField(
    max_length=15,
    validators=[UniqueValidator(queryset=User.objects.all(), message='This username is already taken')]
    )

    password = serializers.CharField(min_length=8, write_only=True)

    profile_picture = Base64ImageField(max_length=None, use_url=True, required=False, write_only=True)

    profile = PKField(read_only=True, source='profile_picture')

    has_picture = serializers.SerializerMethodField('has_profile_picture', read_only = True)
    #img_link = serializers.SerializerMethodField('get_photo_url')

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'profile_picture', 'profile', 'has_picture')

    def create(self, validated_data):
        try:
            image_data = validated_data.pop('profile_picture')
        except:
            image_data = None

        user = User.objects.create_user(**validated_data)
        if image_data is not None:
            userProfile = UserProfile.objects.create(user=user, image=image_data)
        else:
            userProfile = UserProfile.objects.create(user=user)
        return user

    def get_photo_url(self, user):
        try:
            profilePicUrl = user.profile_picture.image.url
            return self.context.get('request').build_absolute_uri(profilePicUrl)
        except:
            return None

    def has_profile_picture(self, user):
        return bool(user.profile_picture.image)


class UserSerializer(QueryFieldsMixin, serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    adverts = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    profile = PKField(read_only=True, source='profile_picture')
    profile_picture = Base64ImageField(max_length=None, use_url=True, required=False, write_only=True)
    has_picture = serializers.SerializerMethodField('has_profile_picture', read_only = True)
    #img_link = serializers.SerializerMethodField('get_photo_url', read_only=True)
    sold_books = serializers.SerializerMethodField('calculate_sold', read_only = True)
    bought_books = serializers.SerializerMethodField('calculate_bought', read_only = True)
    email = serializers.EmailField(
    required=False,
    validators=[UniqueValidator(queryset=User.objects.all(), message='This email is already taken')]
    )
    username = serializers.CharField(
    required=False,
    max_length=15,
    validators=[UniqueValidator(queryset=User.objects.all(), message='This username is already taken')]
    )

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'adverts', 'profile_picture', 'profile', 'has_picture', 'sold_books', 'bought_books')

    @staticmethod
    def setup_eager_loading(queryset, *args):
        """ Perform necessary eager loading of data. """
        #Ta in alla adverts och läs in 'owner och 'responder' i cahce
        advert_queryset = Advert.objects.select_related('responder', 'owner').only('transaction_type', 'state', 'responder', 'owner', 'id')
        for arg in args:
            #Kollar om det är OneToOne eller OneToMany relationship
            if isinstance(User._meta.get_field(arg),type(User._meta.get_field('profile_picture'))):
                queryset = queryset.select_related(arg)
            else:
                if arg == 'adverts':
                    queryset = queryset.prefetch_related(Prefetch(
                    "adverts",
                    queryset=advert_queryset
                    )).prefetch_related('adverts__responder')
                elif arg == 'accepted_adverts':
                    queryset = queryset.prefetch_related(Prefetch(
                    "accepted_adverts",
                    queryset=advert_queryset
                    ))
        return queryset

    def has_profile_picture(self, user):
        return bool(user.profile_picture.image)

    def calculate_sold(self, user):
        sum = len([sold_advert for sold_advert in user.adverts.all() if sold_advert.transaction_type == 'S' and sold_advert.state == 'I' and sold_advert.responder is not None])
        sum += len([sold_advert for sold_advert in user.accepted_adverts.all() if sold_advert.transaction_type == 'B' and sold_advert.state == 'I'])
        return sum

    def calculate_bought(self, user):
        sum = len([bought_advert for bought_advert in user.adverts.all() if bought_advert.transaction_type == 'B' and bought_advert.state == 'I' and bought_advert.responder is not None])
        sum += len([bought_advert for bought_advert in user.accepted_adverts.all() if bought_advert.transaction_type == 'S' and bought_advert.state == 'I'])
        return sum

    def get_photo_url(self, user):
        try:
            profilePicUrl = user.profile_picture.image.url
            return self.context.get('request').build_absolute_uri(profilePicUrl)
        except:
            return None


    def update(self, user, validated_data):
        try:
            image_data = validated_data.pop('profile_picture')
        except:
            image_data = None

        if image_data is not None:
            userProfile = user.profile_picture
            userProfile.image = image_data
            userProfile.save()
        return super(UserSerializer, self).update(user,validated_data)

class ImageSerializer(serializers.ModelSerializer):
    image = Base64ImageField(max_length=None, use_url=True, required=False, write_only=True)

    class Meta:
        model = UserProfile
        fields = ('image', 'user')
