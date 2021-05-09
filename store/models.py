from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

# Create your models here.
from django.utils import timezone


class Book(models.Model):
    title = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    author_name = models.CharField(max_length=255)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='my_books')
    readers = models.ManyToManyField(User, through='UserBookRelation', related_name='books')
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=None, null=True)

    def __str__(self):
        return f'id:{self.id}, title:{self.title}, price:{self.price}'


class Article(models.Model):
    title = models.CharField(max_length=255)
    author_name = models.CharField(max_length=255)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='articles')
    readers = models.ManyToManyField(User, through='UserArticleRelation', related_name='readed_articles')
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=None, null=True)
    date_of_creating = models.DateTimeField(auto_now_add=True)
    date_of_last_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'id:{self.id}, title:{self.title}'


class Review(models.Model):
    title = models.CharField(max_length=255)
    text = models.TextField(max_length=10_000)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, null=True, related_name='reviews')
    author_name = models.CharField(max_length=255)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='my_reviews')
    readers = models.ManyToManyField(User, through='UserReviewRelation', related_name='reviews')
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=None, null=True)

    def __str__(self):
        return f'id:{self.id}, title:{self.title}'


class Discussion(models.Model):
    problem_topic = models.CharField(max_length=255)
    text = models.TextField(max_length=10_000)
    author_name = models.CharField(max_length=255)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='my_discussions')
    readers = models.ManyToManyField(User, through='UserDiscussionRelation', related_name='discussions')
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=None, null=True)

    def __str__(self):
        return f'id:{self.id}, title:{self.problem_topic}'


class Comment(models.Model):
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='my_comments')
    readers = models.ManyToManyField(User, through='UserCommentRelation', related_name='comments')
    obj_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    obj_id = models.PositiveIntegerField()
    obj = GenericForeignKey('obj_type', 'obj_id')

    def __str__(self):
        return f'id:{self.id}, title:{self.owner}'


class UserCommentRelation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_with_comment')
    comment = models.ForeignKey(Comment, on_delete=models.SET_NULL, null=True, related_name='comment_with_user')
    like = models.BooleanField(default=True)


class UserDiscussionRelation(models.Model):
    RATE_CHOICES = (
            (1, 'Ok'),
            (2, 'Fine'),
            (3, 'Good'),
            (4, 'Amazing'),
            (5, 'Incredible'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_with_discussion')
    discussion = models.ForeignKey(Discussion, on_delete=models.SET_NULL, null=True,
                                   related_name='discussion_with_user')
    like = models.BooleanField(default=True)
    rate = models.PositiveSmallIntegerField(choices=RATE_CHOICES, null=True)

    def save(self, *args, **kwargs):
        from store.logic import set_rating
        creating = not self.pk
        old_rating = self.rate
        super().save(*args, **kwargs)
        new_rating = self.rate
        if old_rating != new_rating or creating:
            set_rating(self.discussion, UserReviewRelation, 'review')


class UserArticleRelation(models.Model):
    RATE_CHOICES = (
            (1, 'Ok'),
            (2, 'Fine'),
            (3, 'Good'),
            (4, 'Amazing'),
            (5, 'Incredible'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_with_article')
    article = models.ForeignKey(Article, on_delete=models.SET_NULL, null=True, related_name='article_with_user')
    like = models.BooleanField(default=True)
    in_bookmarks = models.BooleanField(default=True)
    rate = models.PositiveSmallIntegerField(choices=RATE_CHOICES, null=True)

    def __str__(self):
        return f'{self.user} ➤ "{self.article.title}", RATE: {self.rate}'

    def save(self, *args, **kwargs):
        from store.logic import set_rating
        creating = not self.pk
        old_rating = self.rate
        super().save(*args, **kwargs)
        new_rating = self.rate
        if old_rating != new_rating or creating:
            set_rating(self.article, UserArticleRelation, 'article')


class UserBookRelation(models.Model):
    RATE_CHOICES = (
            (1, 'Ok'),
            (2, 'Fine'),
            (3, 'Good'),
            (4, 'Amazing'),
            (5, 'Incredible'),
    )

    def __str__(self):
        return f'{self.user} ➤ "{self.book.title}", RATE: {self.rate}'

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_with_book')
    book = models.ForeignKey(Book, on_delete=models.SET_NULL, null=True, related_name='book_with_user')
    like = models.BooleanField(default=True)
    in_bookmarks = models.BooleanField(default=True)
    rate = models.PositiveSmallIntegerField(choices=RATE_CHOICES, null=True)

    def save(self, *args, **kwargs):
        from store.logic import set_rating
        creating = not self.pk
        old_rating = self.rate
        super().save(*args, **kwargs)
        new_rating = self.rate
        if old_rating != new_rating or creating:
            set_rating(self.book, UserBookRelation, 'book')


class UserReviewRelation(models.Model):
    RATE_CHOICES = (
            (1, 'Ok'),
            (2, 'Fine'),
            (3, 'Good'),
            (4, 'Amazing'),
            (5, 'Incredible'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_with_review')
    review = models.ForeignKey(Review, on_delete=models.SET_NULL, null=True, related_name='review_with_user')
    like = models.BooleanField(default=True)
    rate = models.PositiveSmallIntegerField(choices=RATE_CHOICES, null=True)

    def __str__(self):
        return f'{self.user} ➤ "{self.review.title}", RATE: {self.rate}'

    def save(self, *args, **kwargs):
        from store.logic import set_rating
        creating = not self.pk
        old_rating = self.rate
        super().save(*args, **kwargs)
        new_rating = self.rate
        if old_rating != new_rating or creating:
            set_rating(self.review, UserReviewRelation, 'review')
