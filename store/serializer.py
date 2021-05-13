from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from store.models import Book, UserBookRelation, Article, \
    UserArticleRelation, UserCommentRelation, \
    Comment, Discussion, Review, UserDiscussionRelation, UserReviewRelation


class ReaderSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ("first_name", "last_name")


class BooksSerializer(ModelSerializer):
    annotated_likes = serializers.IntegerField(read_only=True)
    rating = serializers.DecimalField(max_digits=3, decimal_places=2, read_only=True)
    owner_name = serializers.CharField(source='owner.username', default="", read_only=True)
    readers = ReaderSerializer(many=True, read_only=True)

    class Meta:
        model = Book
        fields = ("id", "title", "price", "author_name", "annotated_likes", "rating", "owner_name",
                  "readers"
                  )


class ArticleSerializer(ModelSerializer):
    annotated_likes = serializers.IntegerField(read_only=True)
    rating = serializers.DecimalField(max_digits=3, decimal_places=2, read_only=True)
    owner_name = serializers.CharField(source='owner.username', default="", read_only=True)
    readers = ReaderSerializer(many=True, read_only=True)

    class Meta:
        model = Article
        fields = (
            "id", "title", "author_name", "annotated_likes", "rating", "owner_name",
            "readers", "date_of_creating", "date_of_last_update"
        )


class ReviewSerializer(ModelSerializer):
    annotated_likes = serializers.IntegerField(read_only=True)
    rating = serializers.DecimalField(max_digits=3, decimal_places=2, read_only=True)
    owner_name = serializers.CharField(source='owner.username', default="", read_only=True)
    readers = ReaderSerializer(many=True, read_only=True)

    class Meta:
        model = Review
        fields = ("id", "title", "text", "author_name", "annotated_likes", "rating", "owner_name",
                  "readers")


class DiscussionSerializer(ModelSerializer):
    annotated_likes = serializers.IntegerField(read_only=True)
    rating = serializers.DecimalField(max_digits=3, decimal_places=2, read_only=True)
    owner_name = serializers.CharField(source='owner.username', default="", read_only=True)
    readers = ReaderSerializer(many=True, read_only=True)

    class Meta:
        model = Discussion
        fields = ("id", "problem_topic", "text", "author_name", "annotated_likes", "rating", "owner_name",
                  "readers")


class CommentSerializer(ModelSerializer):
    annotated_likes = serializers.IntegerField(read_only=True)
    owner_name = serializers.CharField(source='owner.username', default="", read_only=True)
    readers = ReaderSerializer(many=True, read_only=True)

    class Meta:
        model = Comment
        fields = ("id", "annotated_likes", "owner_name",
                  "readers", "obj"
                  )


class UserBookRelationSerializer(ModelSerializer):
    class Meta:
        model = UserBookRelation
        fields = ("book", "like", "in_bookmarks", "rate")


class UserArticleRelationSerializer(ModelSerializer):
    class Meta:
        model = UserArticleRelation
        fields = ("article", "like", "in_bookmarks", "rate")


class UserCommentRelationSerializer(ModelSerializer):
    class Meta:
        model = UserCommentRelation

    fields = ("comment", "like")


class UserDiscussionRelationSerializer(ModelSerializer):
    class Meta:
        model = UserDiscussionRelation

    fields = ("discussion", "like", "rate")


class UserReviewRelationSerializer(ModelSerializer):
    class Meta:
        model = UserReviewRelation

    fields = ("review", "like", "rate")
