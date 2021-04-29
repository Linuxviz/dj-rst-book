import json

from django.contrib.auth.models import User
from django.db.models import Count, Case, When
from django.urls import reverse
from rest_framework import response, status
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APITestCase

from store.serializer import BooksSerializer

from store.models import Book, UserBookRelation


class BooksAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username='test_username')
        self.book_1 = Book.objects.create(title="Some title", price='2500.00', author_name="rick", owner=self.user)
        self.book_2 = Book.objects.create(title="Some book", price='300.00', author_name="pick", owner=self.user)
        self.book_3 = Book.objects.create(title="Some book1", price='25', author_name="sam", owner=self.user)
        self.book_4 = Book.objects.create(title="Some book2 rick", price='10000', author_name="tom", owner=self.user)
        self.book_5 = Book.objects.create(title="Dead souls", price='150', author_name="jhon lemon", owner=self.user)

    def test_get(self):
        url = reverse("book-list")
        response = self.client.get(url)
        queryset = Book.objects.all().annotate(
                annotated_likes=Count(Case(When(book_with_user__like=True, then=1)))).order_by('id')
        serializer_data = BooksSerializer(queryset,
                                          many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_get_search(self):
        url = reverse("book-list")
        response = self.client.get(url, data={'search': 'rick'})
        queryset = Book.objects.filter(id__in=[self.book_1.id, self.book_4.id]).annotate(
                annotated_likes=Count(Case(When(book_with_user__like=True, then=1)))).order_by('id')
        serializer_data = BooksSerializer(queryset, many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_create(self):
        self.assertEqual(5, Book.objects.all().count())
        url = reverse("book-list")
        self.client.force_login(self.user)
        response = self.client.post(url,
                                    data=json.dumps(
                                            {
                                                    'title':       'Sherlock Homes',
                                                    'price':       '350.00',
                                                    'author_name': 'conan doyle',

                                            }
                                    ), content_type='application/json'
                                    )
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(6, Book.objects.all().count())
        self.assertEqual(self.user, Book.objects.last().owner)

    def test_update(self):
        url = reverse("book-detail", args=(self.book_1.pk,))
        self.client.force_login(self.user)
        response = self.client.put(url,
                                   data=json.dumps(
                                           {
                                                   'title':       self.book_1.title,
                                                   'price':       8000.00,
                                                   'author_name': self.book_1.author_name
                                           }
                                   ), content_type='application/json'
                                   )
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.book_1.refresh_from_db()
        self.assertEqual(8000, self.book_1.price)

    def test_update_not_owner(self):
        self.user2 = User.objects.create(username='test_username2')
        url = reverse("book-detail", args=(self.book_1.pk,))
        self.client.force_login(self.user2)
        response = self.client.put(url,
                                   data=json.dumps(
                                           {
                                                   'title':       self.book_1.title,
                                                   'price':       8000.00,
                                                   'author_name': self.book_1.author_name
                                           }
                                   ), content_type='application/json'
                                   )
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
        self.book_1.refresh_from_db()
        self.assertEqual(
                {'detail': ErrorDetail(string='You do not have permission to perform this action.',
                                       code='permission_denied')},
                response.data)
        self.assertEqual(2500.00, self.book_1.price)

    def test_update_not_owner_but_staff(self):
        self.user2 = User.objects.create(username='test_username2', is_staff=True)
        url = reverse("book-detail", args=(self.book_1.pk,))
        self.client.force_login(self.user2)
        response = self.client.put(url,
                                   data=json.dumps(
                                           {
                                                   'title':       self.book_1.title,
                                                   'price':       8000.00,
                                                   'author_name': self.book_1.author_name
                                           }
                                   ), content_type='application/json'
                                   )
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.book_1.refresh_from_db()
        self.assertEqual(8000, self.book_1.price)

    # тест на удаление объекта

    def test_delete(self):
        url = reverse("book-detail", args=(self.book_1.pk,))
        self.client.force_login(self.user)
        self.assertEqual(5, Book.objects.all().count())
        response = self.client.delete(url)
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
        self.assertEqual(4, Book.objects.all().count())
        self.assertEqual(False, Book.objects.filter(pk=self.book_1.pk).exists())


class BooksRelationsAPITestCase(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create(username='test_username1')
        self.user2 = User.objects.create(username='test_username2')
        self.book_1 = Book.objects.create(title="Some title", price='2500.00', author_name="rick", owner=self.user1)
        self.book_2 = Book.objects.create(title="Some book", price='300.00', author_name="pick", owner=self.user1)

    def test_like(self):
        url = reverse("userbookrelation-detail", args=(self.book_1.pk,))
        data = json.dumps(
                {
                        'like': True,
                }
        )
        self.client.force_login(self.user1)
        response = self.client.patch(url, data=data,
                                     content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        relation = UserBookRelation.objects.get(user=self.user1, book=self.book_1)
        self.assertTrue(relation.like)

        data = json.dumps(
                {
                        'in_bookmarks': True,
                }
        )
        response = self.client.patch(url, data=data,
                                     content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        relation = UserBookRelation.objects.get(user=self.user1, book=self.book_1)
        self.assertTrue(relation.in_bookmarks)

    def test_rate(self):
        url = reverse("userbookrelation-detail", args=(self.book_1.pk,))
        data = json.dumps(
                {
                        'rate': 3,
                }
        )
        self.client.force_login(self.user1)
        response = self.client.patch(url, data=data,
                                     content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        relation = UserBookRelation.objects.get(user=self.user1, book=self.book_1)
        self.assertEqual(3, relation.rate)

    def test_rate_wrong(self):
        url = reverse("userbookrelation-detail", args=(self.book_1.pk,))
        data = json.dumps(
                {
                        'rate': 6,
                }
        )
        self.client.force_login(self.user1)
        response = self.client.patch(url, data=data,
                                     content_type='application/json')
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
