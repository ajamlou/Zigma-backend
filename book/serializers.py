from rest_framework import serializers
from .models import Book

class BookSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()

    book_title = serializers.CharField(min_length=1,
                                    max_length=250,)

    ISBN = serializers.CharField(min_length=8,
                                max_length=20,
                                required=False)

    authors = serializers.CharField(min_length=1,
                                    max_length=250,
                                    required = False)

    edition = serializers.CharField(min_length=0,
                                    max_length=250,
                                    required=False)

    class Meta:
        model = Book
        fields = (
        'id',
        'ISBN',
        'book_title',
        'authors',
        'edition',
        )
