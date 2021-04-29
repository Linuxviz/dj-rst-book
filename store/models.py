from django.contrib.auth.models import User
from django.db import models


# Create your models here.


class Book(models.Model):
    title = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    author_name = models.CharField(max_length=255)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='my_books')
    readers = models.ManyToManyField(User, through='UserBookRelation', related_name='books')

    def __str__(self):
        return f'id:{self.id}, title:{self.title}, price:{self.price}'


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
