from django.test import TestCase

from store.models import Book
from store.serializer import BooksSerializer


class BookSerializerTestCase(TestCase):
    def test_ok(self):
        book_1 = Book.objects.create(title="Some title", price=2500.00, author_name='jhon')
        book_2 = Book.objects.create(title="Some book", price=300.00, author_name='lemon')
        serializer_data = BooksSerializer([book_1, book_2], many=True).data
        expected_data = [
                {
                        'id':          book_1.id,
                        'title':       "Some title",
                        'price':       '2500.00',
                        'author_name': 'jhon'
                },
                {
                        'id':          book_2.id,
                        'title':       "Some book",
                        'price':       '300.00',
                        'author_name': 'lemon'
                }
        ]
        self.assertEqual(expected_data, serializer_data)
