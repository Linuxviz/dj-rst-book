from django.contrib import admin

# Register your models here.
from django.contrib.admin import ModelAdmin

from store.models import Book, UserBookRelation, Article, Review, Discussion, UserDiscussionRelation, \
    UserArticleRelation, UserReviewRelation, Comment, UserCommentRelation


@admin.register(Book)
class BookAdmin(ModelAdmin):
    pass


@admin.register(Article)
class ArticleAdmin(ModelAdmin):
    pass


@admin.register(Review)
class ReviewAdmin(ModelAdmin):
    pass


@admin.register(Discussion)
class DiscussionAdmin(ModelAdmin):
    pass


@admin.register(Comment)
class CommentAdmin(ModelAdmin):
    pass


@admin.register(UserBookRelation)
class UserBookRelationAdmin(ModelAdmin):
    pass


@admin.register(UserDiscussionRelation)
class UserDiscussionRelationAdmin(ModelAdmin):
    pass


@admin.register(UserArticleRelation)
class UserArticleRelationAdmin(ModelAdmin):
    pass


@admin.register(UserReviewRelation)
class UserReviewRelationAdmin(ModelAdmin):
    pass


@admin.register(UserCommentRelation)
class UserCommentRelationAdmin(ModelAdmin):
    pass
