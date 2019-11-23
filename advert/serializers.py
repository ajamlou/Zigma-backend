from rest_framework import serializers
from .models import Advert, AdvertImage
from drf_extra_fields.fields import Base64ImageField
from django.contrib.auth.models import User
from user.models import UserProfile
from drf_queryfields import QueryFieldsMixin
from django.db.models import Prefetch


class PKField(serializers.RelatedField):
    def to_representation(self,instance):
        return instance.pk

class AdvertImageSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    class Meta:
        model = AdvertImage
        fields = (
        'id',
        'image',
        'advert',
        )

class AdvertPostSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()

    image = serializers.ListField(child=Base64ImageField(required=False,
                                use_url=True,
                                max_length=None),
                                write_only=True,
                                required=False)

    owner = serializers.PrimaryKeyRelatedField(required=False,
                                    queryset=User.objects.all(),
                                    write_only=True)

    price = serializers.IntegerField(min_value=0,
                                    max_value=9999,
                                    write_only=True)

    book_title = serializers.CharField(min_length=1,
                                    max_length=250,
                                    write_only=True)

    ISBN = serializers.CharField(min_length=8,
                                max_length=20,
                                write_only=True,
                                required=False)

    authors= serializers.CharField(min_length=1,
                                    max_length=250,
                                    write_only=True,
                                    required = False)

    edition = serializers.CharField(min_length=0,
                                    max_length=250,
                                    write_only=True,
                                    required=False)

    condition = serializers.CharField(min_length=1,
                                    max_length=1,
                                    write_only=True,
                                    required=False,)

    state = serializers.CharField(min_length=1,
                                    max_length=1,
                                    write_only=True,
                                    required=False)

    transaction_type = serializers.CharField(min_length=1,
                                    max_length=1,
                                    write_only=True,
                                    required=False)

    contact_info = serializers.CharField(min_length=0,
                                    max_length=250,
                                    write_only=True,
                                    required=True)

    class Meta:
        model = Advert
        fields = (
        'id',
        'owner',
        'price',
        'book_title',
        'ISBN',
        'authors',
        'edition',
        'condition',
        'state',
        'transaction_type',
        'contact_info',
        'image')

    @staticmethod
    def setup_eager_loading(queryset):
        """ Perform necessary eager loading of data. """
        queryset = queryset.prefetch_related('image')
        return queryset

    def create(self, validated_data):
        try:
            image_data = validated_data.pop('image')
        except:
            image_data = None

        advert = Advert.objects.create(**validated_data)

        if image_data is not None:
            for image in image_data:
                im = AdvertImage.objects.create(image=image,advert=advert)
        return advert

class AdvertSerializer(QueryFieldsMixin, serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    image = PKField(many=True, read_only=True)
    new_images = serializers.ListField(child=Base64ImageField(required=False,
                                use_url=True,
                                max_length=None),
                                write_only=True,
                                required=False)
    delete_images = serializers.PrimaryKeyRelatedField(queryset=AdvertImage.objects.all(),many=True, write_only=True)
    condition = serializers.CharField(source='get_condition_display')
    #image = serializers.SerializerMethodField('get_image_url')
    #owner = serializers.ReadOnlyField(source='owner.id')

    class Meta:
        model = Advert
        fields = (
        'id',
        'owner',
        'price',
        'book_title',
        'ISBN',
        'authors',
        'edition',
        'condition',
        'state',
        'transaction_type',
        'contact_info',
        'image',
        'new_images',
        'delete_images',
        'created_at')

    def update(self, advert, validated_data):
        try:
            image_data = validated_data.pop('new_images')
        except:
            image_data = None

        if image_data is not None:
            for image in image_data:
                AdvertImage.objects.create(advert=advert,image=image)
        try:
            images = validated_data.pop('delete_images')
        except:
            images = None

        if images is not None:
            for image in images:
                image.delete()
            #AdvertImage.objects.filter(pk__in=image_pks).delete()

        return super(self.__class__,self).update(advert, validated_data)

    @staticmethod
    def setup_eager_loading(queryset):
        """ Perform necessary eager loading of data. """
        queryset = queryset.prefetch_related(\
        Prefetch(\
        'image', queryset=AdvertImage.objects.all().only('pk','advert_id')))\
        .select_related('owner')\
        .defer('responder', 'owner__email','owner__password','owner__first_name',\
         'owner__last_name', 'owner__username', 'owner__last_login','owner__is_superuser',\
         'owner__is_staff', 'owner__is_active', 'owner__date_joined')
        return queryset

    #def get_image_url(self,advert):


class AdvertRetrieveSerializer(QueryFieldsMixin, serializers.ModelSerializer):
    image = PKField(many=True, read_only=True)
    owner = serializers.ReadOnlyField(source='owner.id')
    condition = serializers.CharField(source='get_condition_display')
    # state = serializers.CharField(source='get_state_display')


    class Meta:
        model = Advert
        fields = (
        'id',
        'owner',
        'price',
        'book_title',
        'ISBN',
        'authors',
        'edition',
        'condition',
        'state',
        'transaction_type',
        'contact_info',
        'image',
        'created_at',
        )

    @staticmethod
    def setup_eager_loading(queryset):
        """ Perform necessary eager loading of data. """
        queryset = queryset.select_related('owner')\
        .prefetch_related('image')
        return queryset
