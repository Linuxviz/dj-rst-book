from django.urls import reverse
from rest_framework import response, status
from rest_framework.test import APITestCase

from store.serializer import BooksSerializer

from store.models import Book


class BooksAPITestCase(APITestCase):
    def setUp(self):
        self.book_1 = Book.objects.create(title="Some title", price='2500.00', author_name="rick")
        self.book_2 = Book.objects.create(title="Some book", price='300.00', author_name="pick")
        self.book_3 = Book.objects.create(title="Some book1", price='25', author_name="sam")
        self.book_4 = Book.objects.create(title="Some book2 rick", price='10000', author_name="tom")
        self.book_5 = Book.objects.create(title="Dead souls", price='150', author_name="jhon lemon")

    def test_get(self):
        url = reverse("book-list")
        response = self.client.get(url)
        serializer_data = BooksSerializer([self.book_1, self.book_2, self.book_3, self.book_4, self.book_5],
                                          many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_get_search(self):
        url = reverse("book-list")
        response = self.client.get(url, data={'search': 'rick'})
        serializer_data = BooksSerializer([self.book_1, self.book_4], many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)
