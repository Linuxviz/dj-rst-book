from django.contrib.auth.models import User
from django.db.models import Count, Case, When, Avg
from django.test import TestCase

from store.models import Book, UserBookRelation
from store.serializer import BooksSerializer


class BookSerializerTestCase(TestCase):
    def test_ok(self):
        self.user1 = User.objects.create(username='test_username1', first_name='petr', last_name='letor')
        self.user2 = User.objects.create(username='test_username2', first_name='metr', last_name='heiter')
        self.user3 = User.objects.create(username='test_username3', )
        book_1 = Book.objects.create(title="Some title", price='2500.00', author_name='jhon', owner=self.user1)
        book_2 = Book.objects.create(title="Some book", price='300.00', author_name='lemon')

        ur1 = UserBookRelation.objects.create(user=self.user1, book=book_1, like=True, rate=3)
        ur2 = UserBookRelation.objects.create(user=self.user2, book=book_1, like=True, rate=3)
        ur3 = UserBookRelation.objects.create(user=self.user3, book=book_1, like=True)
        ur3.rate = 3
        ur3.save()

        ur4 = UserBookRelation.objects.create(user=self.user1, book=book_2, like=True, rate=5)
        ur5 = UserBookRelation.objects.create(user=self.user2, book=book_2, like=True, rate=2)
        ur6 = UserBookRelation.objects.create(user=self.user3, book=book_2, like=False)

        books = Book.objects.all().annotate(
                annotated_likes=Count(Case(When(book_with_user__like=True, then=1))),
        ).order_by('id')

        serializer_data = BooksSerializer(books, many=True).data
        expected_data = [
                {
                        'id':              book_1.id,
                        'title':           'Some title',
                        'price':           '2500.00',
                        'author_name':     'jhon',
                        'annotated_likes': 3,
                        'rating':          '3.67',
                        'owner_name':      'test_username1',
                        'readers':         [
                                {
                                        "first_name": 'petr',
                                        "last_name":  'letor',
                                },
                                {
                                        "first_name": 'metr',
                                        "last_name":  'heiter',
                                },
                                {
                                        "first_name": '',
                                        "last_name":  '',
                                },
                        ]
                },
                {
                        'id':              book_2.id,
                        'title':           'Some book',
                        'price':           '300.00',
                        'author_name':     'lemon',
                        'annotated_likes': 2,
                        'rating':          '3.50',
                        "owner_name":      '',
                        'readers':         [
                                {
                                        "first_name": 'petr',
                                        "last_name":  'letor',
                                },
                                {
                                        "first_name": 'metr',
                                        "last_name":  'heiter',
                                },
                                {
                                        "first_name": '',
                                        "last_name":  '',
                                },
                        ]
                }
        ]
        print(serializer_data)
        self.assertEqual(expected_data, serializer_data)
