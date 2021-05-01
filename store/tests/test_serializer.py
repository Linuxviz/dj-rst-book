from django.contrib.auth.models import User
from django.db.models import Count, Case, When, Avg
from django.test import TestCase

from store.models import Book, UserBookRelation
from store.serializer import BooksSerializer


class BookSerializerTestCase(TestCase):
    def test_ok(self):
        self.user1 = User.objects.create(username='test_username1')
        self.user2 = User.objects.create(username='test_username2')
        self.user3 = User.objects.create(username='test_username3')
        book_1 = Book.objects.create(title="Some title", price='2500.00', author_name='jhon')
        book_2 = Book.objects.create(title="Some book", price='300.00', author_name='lemon')

        ur1 = UserBookRelation.objects.create(user=self.user1, book=book_1, like=True, rate=3)
        ur2 = UserBookRelation.objects.create(user=self.user2, book=book_1, like=True, rate=3)
        ur3 = UserBookRelation.objects.create(user=self.user3, book=book_1, like=True, rate=5)

        ur4 = UserBookRelation.objects.create(user=self.user1, book=book_2, like=True, rate=5)
        ur5 = UserBookRelation.objects.create(user=self.user2, book=book_2, like=True, rate=2)
        ur6 = UserBookRelation.objects.create(user=self.user3, book=book_2, like=False)

        books = Book.objects.all().annotate(
                annotated_likes=Count(Case(When(book_with_user__like=True, then=1))),
                rating=Avg('book_with_user__rate')
        ).order_by('id')

        serializer_data = BooksSerializer(books, many=True).data
        expected_data = [
                {
                        'id':              book_1.id,
                        'title':           'Some title',
                        'price':           '2500.00',
                        'author_name':     'jhon',
                        'likes_count':     3,
                        'annotated_likes': 3,
                        'rating':          '3.67'
                },
                {
                        'id':              book_2.id,
                        'title':           'Some book',
                        'price':           '300.00',
                        'author_name':     'lemon',
                        'likes_count':     2,
                        'annotated_likes': 2,
                        'rating':          '3.50'
                }
        ]
        print(serializer_data)
        self.assertEqual(expected_data, serializer_data)
