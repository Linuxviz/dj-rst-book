import json

from django.contrib.auth.models import User
from django.db import connection
from django.db.models import Count, Case, When
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APITestCase

from store.models import Book, UserBookRelation, Article, UserArticleRelation, Review, UserReviewRelation, Discussion, \
    UserDiscussionRelation
from store.serializer import BooksSerializer, ArticleSerializer, ReviewSerializer, DiscussionSerializer


class BooksAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username='test_username')
        self.book_1 = Book.objects.create(title="Some title", price='2500.00', author_name="rick", owner=self.user)
        self.book_2 = Book.objects.create(title="Some book", price='300.00', author_name="pick", owner=self.user)
        self.book_3 = Book.objects.create(title="Some book1", price='25', author_name="sam", owner=self.user)
        self.book_4 = Book.objects.create(title="Some book2 rick", price='10000', author_name="tom", owner=self.user)
        self.book_5 = Book.objects.create(title="Dead souls", price='150', author_name="jhon lemon", owner=self.user)
        ur1 = UserBookRelation.objects.create(user=self.user, book=self.book_1, like=True, rate=5)

    def test_get(self):
        url = reverse("book-list")
        with CaptureQueriesContext(connection) as queries:
            response = self.client.get(url)
            self.assertEqual(2, len(queries), "Изменилось количество запросов")
        queryset = Book.objects.all().annotate(
            annotated_likes=Count(Case(When(book_with_user__like=True, then=1))),
        ).order_by('id')
        serializer_data = BooksSerializer(queryset,
                                          many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)
        self.assertEqual(serializer_data[0]['rating'], "5.00")
        self.assertEqual(serializer_data[0]['annotated_likes'], 1)

    def test_get_search(self):
        url = reverse("book-list")
        response = self.client.get(url, data={'search': 'rick'})
        queryset = Book.objects.filter(id__in=[self.book_1.id, self.book_4.id]).annotate(
            annotated_likes=Count(Case(When(book_with_user__like=True, then=1))),
        ).order_by('id')
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
                                            'title': 'Sherlock Homes',
                                            'price': '350.00',
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
                                           'title': self.book_1.title,
                                           'price': 8000.00,
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
                                           'title': self.book_1.title,
                                           'price': 8000.00,
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
                                           'title': self.book_1.title,
                                           'price': 8000.00,
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


class ArticleAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username='test_username')
        self.user2 = User.objects.create(username='test_username_2')
        self.user3 = User.objects.create(username='test_username_3')
        self.article_1 = Article.objects.create(title="Some title", author_name="rick", owner=self.user)
        self.article_2 = Article.objects.create(title="Some book", author_name="pick", owner=self.user)
        self.article_3 = Article.objects.create(title="Some book1", author_name="sam", owner=self.user)
        self.article_4 = Article.objects.create(title="Some book2 rick", author_name="tom", owner=self.user)
        self.article_5 = Article.objects.create(title="Dead souls", author_name="jhon lemon", owner=self.user)
        self.ur1 = UserArticleRelation.objects.create(user=self.user, article=self.article_1, like=True, rate=5)
        self.ur2 = UserArticleRelation.objects.create(user=self.user3, article=self.article_1, like=True, rate=3)

    def test_get(self):
        url = reverse("article-list")
        response = self.client.get(url)
        queryset = Article.objects.all().annotate(
            annotated_likes=Count(Case(When(article_with_user__like=True, then=1))),
        ).order_by('id')
        serializer_data = ArticleSerializer(queryset,
                                            many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)
        self.assertEqual(serializer_data[0]['rating'], "4.00")
        self.assertEqual(serializer_data[0]['annotated_likes'], 2)

    def test_update(self):
        url = reverse("article-detail", args=(self.article_1.pk,))
        self.client.force_login(self.user)
        response = self.client.put(url,
                                   data=json.dumps(
                                       {
                                           'title': "new_title",
                                           'author_name': self.article_1.author_name
                                       }
                                   ), content_type='application/json'
                                   )
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.article_1.refresh_from_db()
        self.assertEqual("new_title", self.article_1.title)

    def test_create(self):
        self.assertEqual(5, Article.objects.all().count())
        url = reverse("article-list")
        self.client.force_login(self.user)
        response = self.client.post(url,
                                    data=json.dumps(
                                        {
                                            'title': 'about trees',
                                            'author_name': self.user.username,
                                        }
                                    ), content_type='application/json'
                                    )
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(6, Article.objects.all().count())
        self.assertEqual(self.user, Article.objects.last().owner)

    def test_get_search(self):
        url = reverse("article-list")
        response = self.client.get(url, data={'search': 'rick'})
        queryset = Article.objects.filter(id__in=[self.article_1.id, self.article_4.id]).annotate(
            annotated_likes=Count(Case(When(article_with_user__like=True, then=1))),
        ).order_by('id')
        serializer_data = ArticleSerializer(queryset, many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_update_not_owner(self):
        self.user4 = User.objects.create(username='test_username4')
        url = reverse("article-detail", args=(self.article_1.pk,))
        self.client.force_login(self.user4)
        response = self.client.put(url,
                                   data=json.dumps(
                                       {
                                           'title': "new title",
                                           'author_name': self.article_1.author_name,
                                       }
                                   ), content_type='application/json'
                                   )
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
        self.article_1.refresh_from_db()
        self.assertEqual(
            {'detail': ErrorDetail(string='You do not have permission to perform this action.',
                                   code='permission_denied')},
            response.data)
        self.assertEqual("Some title", self.article_1.title)

    def test_update_not_owner_but_staff(self):
        self.user4 = User.objects.create(username='test_username2', is_staff=True)
        url = reverse("article-detail", args=(self.article_1.pk,))
        self.client.force_login(self.user4)
        response = self.client.put(url,
                                   data=json.dumps(
                                       {
                                           'title': "new title",
                                           'author_name': self.article_1.author_name,
                                       }
                                   ), content_type='application/json'
                                   )
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.article_1.refresh_from_db()
        self.assertEqual('new title', self.article_1.title)

    def test_delete(self):
        url = reverse("article-detail", args=(self.article_1.pk,))
        self.client.force_login(self.user)
        self.assertEqual(5, Article.objects.all().count())
        response = self.client.delete(url)
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
        self.assertEqual(4, Article.objects.all().count())
        self.assertEqual(False, Article.objects.filter(pk=self.article_1.pk).exists())


class ReviewAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username='test_username')
        self.book_1 = Book.objects.create(title="Goger moger", price='2500.00', author_name="rick", owner=self.user)
        self.user2 = User.objects.create(username='test_username_2')
        self.user3 = User.objects.create(username='test_username_3')
        self.review_1 = Review.objects.create(title="Some title", text="Some_text", book=self.book_1,
                                              author_name="rick", owner=self.user)
        self.review_2 = Review.objects.create(title="Some book", text="Some_text", book=self.book_1,
                                              author_name="pick", owner=self.user)
        self.review_3 = Review.objects.create(title="Some book1", text="Some_text", book=self.book_1,
                                              author_name="sam", owner=self.user)
        self.review_4 = Review.objects.create(title="Some book2 rick", text="Some_text", author_name="tom",
                                              owner=self.user)
        self.review_5 = Review.objects.create(title="Dead souls", text="Some_text", author_name="jhon lemon",
                                              owner=self.user)
        self.ur1 = UserReviewRelation.objects.create(user=self.user, review=self.review_1, like=True, rate=5)
        self.ur2 = UserReviewRelation.objects.create(user=self.user3, review=self.review_1, like=True, rate=3)

    def test_get(self):
        url = reverse("review-list")
        response = self.client.get(url)
        queryset = Review.objects.all().annotate(
            annotated_likes=Count(Case(When(review_with_user__like=True, then=1))),
        ).order_by('id')
        serializer_data = ReviewSerializer(queryset,
                                           many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)
        self.assertEqual(serializer_data[0]['rating'], "4.00")
        self.assertEqual(serializer_data[0]['annotated_likes'], 2)

    def test_update(self):
        url = reverse("review-detail", args=(self.review_1.pk,))
        self.client.force_login(self.user)
        response = self.client.put(url,
                                   data=json.dumps(
                                       {
                                           'title': "new_title",
                                           'author_name': self.review_1.author_name
                                       }
                                   ), content_type='application/json'
                                   )
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.review_1.refresh_from_db()
        self.assertEqual("new_title", self.review_1.title)

    def test_create(self):
        self.book_2 = Book.objects.create(title="Some title", price='2500.00', author_name="rick", owner=self.user)
        self.assertEqual(5, Review.objects.all().count())
        url = reverse("review-list")
        self.client.force_login(self.user)
        response = self.client.post(url,
                                    data=json.dumps(
                                        {
                                            'book': self.book_2.pk,
                                            'text': 'text',
                                            'title': 'about trees',
                                            'author_name': self.user.username,
                                        }
                                    ), content_type='application/json'
                                    )
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(6, Review.objects.all().count())
        self.assertEqual(self.user, Review.objects.last().owner)

    def test_get_search(self):
        url = reverse("review-list")
        response = self.client.get(url, data={'search': 'rick'})
        queryset = Review.objects.filter(id__in=[self.review_1.id, self.review_4.id]).annotate(
            annotated_likes=Count(Case(When(review_with_user__like=True, then=1))),
        ).order_by('id')
        serializer_data = ReviewSerializer(queryset, many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_update_not_owner(self):
        self.user4 = User.objects.create(username='test_username4')
        url = reverse("review-detail", args=(self.review_1.pk,))
        self.client.force_login(self.user4)
        response = self.client.put(url,
                                   data=json.dumps(
                                       {
                                           'title': "new title",
                                           'author_name': self.review_1.author_name,
                                       }
                                   ), content_type='application/json'
                                   )
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
        self.review_1.refresh_from_db()
        self.assertEqual(
            {'detail': ErrorDetail(string='You do not have permission to perform this action.',
                                   code='permission_denied')},
            response.data)
        self.assertEqual("Some title", self.review_1.title)

    def test_update_not_owner_but_staff(self):
        self.user4 = User.objects.create(username='test_username2', is_staff=True)
        url = reverse("review-detail", args=(self.review_1.pk,))
        self.client.force_login(self.user4)
        response = self.client.put(url,
                                   data=json.dumps(
                                       {
                                           'title': "new title",
                                           'author_name': self.review_1.author_name,
                                       }
                                   ), content_type='application/json'
                                   )
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.review_1.refresh_from_db()
        self.assertEqual('new title', self.review_1.title)

    def test_delete(self):
        url = reverse("review-detail", args=(self.review_1.pk,))
        self.client.force_login(self.user)
        self.assertEqual(5, Review.objects.all().count())
        response = self.client.delete(url)
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
        self.assertEqual(4, Review.objects.all().count())
        self.assertEqual(False, Review.objects.filter(pk=self.review_1.pk).exists())


class DiscussionAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username='test_username')
        self.book_1 = Book.objects.create(title="Goger moger", price='2500.00', author_name="rick", owner=self.user)
        self.user2 = User.objects.create(username='test_username_2')
        self.user3 = User.objects.create(username='test_username_3')
        self.discussion_1 = Discussion.objects.create(problem_topic="Some title", text="Some_text",
                                                      author_name="rick", owner=self.user)
        self.discussion_2 = Discussion.objects.create(problem_topic="Some book", text="Some_text",
                                                      author_name="pick", owner=self.user)
        self.discussion_3 = Discussion.objects.create(problem_topic="Some book1", text="Some_text",
                                                      author_name="sam", owner=self.user)
        self.discussion_4 = Discussion.objects.create(problem_topic="Some book2 rick", text="Some_text",
                                                      author_name="tom",
                                                      owner=self.user)
        self.discussion_5 = Discussion.objects.create(problem_topic="Dead souls", text="Some_text",
                                                      author_name="jhon lemon",
                                                      owner=self.user)
        self.ur1 = UserDiscussionRelation.objects.create(user=self.user, discussion=self.discussion_1, like=True,
                                                         rate=5)
        self.ur2 = UserDiscussionRelation.objects.create(user=self.user3, discussion=self.discussion_1, like=True,
                                                         rate=3)

    def test_get(self):
        url = reverse("discussion-list")
        response = self.client.get(url)
        queryset = Discussion.objects.all().annotate(
            annotated_likes=Count(Case(When(discussion_with_user__like=True, then=1))),
        ).order_by('id')
        serializer_data = DiscussionSerializer(queryset,
                                               many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)
        self.assertEqual(serializer_data[0]['rating'], "4.00")
        self.assertEqual(serializer_data[0]['annotated_likes'], 2)

    def test_update(self):
        url = reverse("discussion-detail", args=(self.discussion_1.pk,))
        self.client.force_login(self.user)
        response = self.client.put(url,
                                   data=json.dumps(
                                       {
                                           'problem_topic': "new_title",
                                           'text': 'text',
                                           'author_name': self.discussion_1.author_name
                                       }
                                   ), content_type='application/json'
                                   )
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.discussion_1.refresh_from_db()
        self.assertEqual("new_title", self.discussion_1.problem_topic)

    def test_create(self):
        self.assertEqual(5, Discussion.objects.all().count())
        url = reverse("discussion-list")
        self.client.force_login(self.user)
        response = self.client.post(url,
                                    data=json.dumps(
                                        {
                                            'text': 'text',
                                            'problem_topic': 'about trees',
                                            'author_name': self.user.username,
                                        }
                                    ), content_type='application/json'
                                    )
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(6, Discussion.objects.all().count())
        self.assertEqual(self.user, Discussion.objects.last().owner)

    def test_get_search(self):
        url = reverse("discussion-list")
        response = self.client.get(url, data={'search': 'rick'})
        queryset = Discussion.objects.filter(id__in=[self.discussion_1.id, self.discussion_4.id]).annotate(
            annotated_likes=Count(Case(When(discussion_with_user__like=True, then=1))),
        ).order_by('id')
        serializer_data = DiscussionSerializer(queryset, many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_update_not_owner(self):
        self.user4 = User.objects.create(username='test_username4')
        url = reverse("discussion-detail", args=(self.discussion_1.pk,))
        self.client.force_login(self.user4)
        response = self.client.put(url,
                                   data=json.dumps(
                                       {
                                           'problem_topic': "new title",
                                           'text': 'text',
                                           'author_name': self.discussion_1.author_name,
                                       }
                                   ), content_type='application/json'
                                   )
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
        self.discussion_1.refresh_from_db()
        self.assertEqual(
            {'detail': ErrorDetail(string='You do not have permission to perform this action.',
                                   code='permission_denied')},
            response.data)
        self.assertEqual("Some title", self.discussion_1.problem_topic)

    def test_update_not_owner_but_staff(self):
        self.user4 = User.objects.create(username='test_username2', is_staff=True)
        url = reverse("discussion-detail", args=(self.discussion_1.pk,))
        self.client.force_login(self.user4)
        response = self.client.put(url,
                                   data=json.dumps(
                                       {
                                           'problem_topic': "new title",
                                           'text': 'text',
                                           'author_name': self.discussion_1.author_name,
                                       }
                                   ), content_type='application/json'
                                   )
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.discussion_1.refresh_from_db()
        self.assertEqual('new title', self.discussion_1.problem_topic)

    def test_delete(self):
        url = reverse("discussion-detail", args=(self.discussion_1.pk,))
        self.client.force_login(self.user)
        self.assertEqual(5, Discussion.objects.all().count())
        response = self.client.delete(url)
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
        self.assertEqual(4, Discussion.objects.all().count())
        self.assertEqual(False, Discussion.objects.filter(pk=self.discussion_1.pk).exists())


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
