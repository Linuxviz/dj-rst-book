from django.db.models import Count, Case, When
from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.mixins import UpdateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet, GenericViewSet

from store.models import Book, UserBookRelation, Article, Comment, Discussion, Review, UserCommentRelation, \
    UserDiscussionRelation, UserArticleRelation, UserReviewRelation
from store.permissions import IsOwnerOrStaffOrReadOnly
from store.serializer import BooksSerializer, UserBookRelationSerializer, ArticleSerializer, \
    UserReviewRelationSerializer, UserArticleRelationSerializer, UserDiscussionRelationSerializer, \
    UserCommentRelationSerializer, CommentSerializer, DiscussionSerializer, ReviewSerializer


class ArticleViewSet(ModelViewSet):
    queryset = Article.objects.annotate(
        annotated_likes=Count(Case(When(article_with_user__like=True, then=1))),
    ).select_related('owner').prefetch_related('readers').order_by('id')
    serializer_class = ArticleSerializer

    def perform_create(self, serializer):
        serializer.validated_data['owner'] = self.request.user
        serializer.save()


class BookViewSet(ModelViewSet):
    queryset = Book.objects.annotate(
        annotated_likes=Count(Case(When(book_with_user__like=True, then=1))),
    ).select_related('owner').prefetch_related('readers').order_by('id')
    serializer_class = BooksSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filter_fields = ['price']  # фильтр сортирует конкретное поле по знаению
    search_fields = ['title', 'author_name']  # поиск позволяет искать все совпадения в указанных полях
    ordering_fields = ['price', 'author_name']
    permission_classes = [IsOwnerOrStaffOrReadOnly]

    def perform_create(self, serializer):
        serializer.validated_data['owner'] = self.request.user
        serializer.save()


class ReviewViewSet(ModelViewSet):
    queryset = Review.objects.annotate(
        annotated_likes=Count(Case(When(review_with_user__like=True, then=1))),
    ).select_related('owner').prefetch_related('readers').order_by('id')
    serializer_class = ReviewSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['title', 'author_name']  # поиск позволяет искать все совпадения в указанных полях
    ordering_fields = ['price', 'author_name']
    permission_classes = [IsOwnerOrStaffOrReadOnly]

    def perform_create(self, serializer):
        serializer.validated_data['owner'] = self.request.user
        serializer.save()


class DiscussionViewSet(ModelViewSet):
    queryset = Discussion.objects.annotate(
        annotated_likes=Count(Case(When(discussion_with_user__like=True, then=1))),
    ).select_related('owner').prefetch_related('readers').order_by('id')
    serializer_class = DiscussionSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['title', 'author_name']  # поиск позволяет искать все совпадения в указанных полях
    ordering_fields = ['price', 'author_name']
    permission_classes = [IsOwnerOrStaffOrReadOnly]

    def perform_create(self, serializer):
        serializer.validated_data['owner'] = self.request.user
        serializer.save()


class CommentViewSet(ModelViewSet):
    queryset = Comment.objects.annotate(
        annotated_likes=Count(Case(When(comment_with_user__like=True, then=1))),
    ).select_related('owner').prefetch_related('readers').order_by('id')
    serializer_class = CommentSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['title', 'author_name']  # поиск позволяет искать все совпадения в указанных полях
    ordering_fields = ['price', 'author_name']
    permission_classes = [IsOwnerOrStaffOrReadOnly]

    def perform_create(self, serializer):
        serializer.validated_data['owner'] = self.request.user
        serializer.save()


class UserBookRelationViewSet(UpdateModelMixin, GenericViewSet):
    permission_classes = [IsAuthenticated]
    queryset = UserBookRelation.objects.all()
    serializer_class = UserBookRelationSerializer
    lookup_field = 'book'

    def get_object(self):
        obj, _ = UserBookRelation.objects.get_or_create(user=self.request.user, book_id=self.kwargs['book'])
        return obj


class UserCommentRelationViewSet(UpdateModelMixin, GenericViewSet):
    permission_classes = [IsAuthenticated]
    queryset = UserCommentRelation.objects.all()
    serializer_class = UserCommentRelationSerializer
    lookup_field = 'comment'

    def get_object(self):
        obj, _ = UserCommentRelation.objects.get_or_create(user=self.request.user, book_id=self.kwargs['comment'])
        return obj


class UserDiscussionRelationViewSet(UpdateModelMixin, GenericViewSet):
    permission_classes = [IsAuthenticated]
    queryset = UserDiscussionRelation.objects.all()
    serializer_class = UserDiscussionRelationSerializer
    lookup_field = 'discussion'

    def get_object(self):
        obj, _ = UserDiscussionRelation.objects.get_or_create(user=self.request.user, book_id=self.kwargs['discussion'])
        return obj


class UserArticleRelationViewSet(UpdateModelMixin, GenericViewSet):
    permission_classes = [IsAuthenticated]
    queryset = UserArticleRelation.objects.all()
    serializer_class = UserArticleRelationSerializer
    lookup_field = 'article'

    def get_object(self):
        obj, _ = UserArticleRelation.objects.get_or_create(user=self.request.user, book_id=self.kwargs['article'])
        return obj


class UserReviewRelationViewSet(UpdateModelMixin, GenericViewSet):
    permission_classes = [IsAuthenticated]
    queryset = UserReviewRelation.objects.all()
    serializer_class = UserReviewRelationSerializer
    lookup_field = 'review'

    def get_object(self):
        obj, _ = UserReviewRelation.objects.get_or_create(user=self.request.user, book_id=self.kwargs['review'])
        return obj


def auth(request):
    return render(request, 'store/oAuth.html')
