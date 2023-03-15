from django.contrib.auth.models import User
from rest_framework import serializers

from store.models import Book, UserBookRelation, Comments


class BookReaderSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name'] 



class BookSerializer(serializers.ModelSerializer):
    annotated_likes = serializers.IntegerField(read_only=True)
    rating = serializers.DecimalField(max_digits=3, decimal_places=2,
                                      read_only=True)
    max_rating = serializers.IntegerField(read_only=True)
    min_rating = serializers.IntegerField(read_only=True)
    count_comments = serializers.IntegerField(read_only=True)
    owner_name = serializers.CharField(read_only=True)
    readers = BookReaderSerializer(many=True, read_only=True)

    class Meta:
        model = Book
        fields = ('id', 'name', 'price', 'author_name','annotated_likes', 
                  'rating', 'max_rating', 'min_rating',
                  'count_comments', 'owner_name', 'readers')


class UserBookRelationSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserBookRelation
        fields = ['book', 'like', 'in_bookmarks', 'rate', 'comment']


class CommentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comments
        fields = ('book', 'text_comment', 'comment_date') 
