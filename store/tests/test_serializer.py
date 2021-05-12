from django.contrib.auth.models import User
from django.db.models import Count, Case, When
from django.test import TestCase

from store.models import Book, UserBookRelation, Review, UserReviewRelation, Article, UserArticleRelation
from store.serializer import BooksSerializer, ReviewSerializer, ArticleSerializer


class BookSerializerTestCase(TestCase):
    def test_ok(self):
        self.user1 = User.objects.create(username='test_username1', first_name='petr', last_name='letor')
        self.user2 = User.objects.create(username='test_username2', first_name='metr', last_name='heiter')
        self.user3 = User.objects.create(username='test_username3', )
        book_1 = Book.objects.create(title="Some title", price='2500.00', author_name='jhon', owner=self.user1)
        book_2 = Book.objects.create(title="Some book", price='300.00', author_name='lemon')

        UserBookRelation.objects.create(user=self.user1, book=book_1, like=True, rate=3)
        UserBookRelation.objects.create(user=self.user2, book=book_1, like=True, rate=3)
        ur3 = UserBookRelation.objects.create(user=self.user3, book=book_1, like=True)
        ur3.rate = 3
        ur3.save()

        UserBookRelation.objects.create(user=self.user1, book=book_2, like=True, rate=5)
        UserBookRelation.objects.create(user=self.user2, book=book_2, like=True, rate=2)
        UserBookRelation.objects.create(user=self.user3, book=book_2, like=False)

        books = Book.objects.all().annotate(
            annotated_likes=Count(Case(When(book_with_user__like=True, then=1))),
        ).order_by('id')

        serializer_data = BooksSerializer(books, many=True).data
        expected_data = [
            {
                'id': book_1.id,
                'title': 'Some title',
                'price': '2500.00',
                'author_name': 'jhon',
                'annotated_likes': 3,
                'rating': '3.00',
                'owner_name': 'test_username1',
                'readers': [
                    {
                        "first_name": 'petr',
                        "last_name": 'letor',
                    },
                    {
                        "first_name": 'metr',
                        "last_name": 'heiter',
                    },
                    {
                        "first_name": '',
                        "last_name": '',
                    },
                ]
            },
            {
                'id': book_2.id,
                'title': 'Some book',
                'price': '300.00',
                'author_name': 'lemon',
                'annotated_likes': 2,
                'rating': '3.50',
                "owner_name": '',
                'readers': [
                    {
                        "first_name": 'petr',
                        "last_name": 'letor',
                    },
                    {
                        "first_name": 'metr',
                        "last_name": 'heiter',
                    },
                    {
                        "first_name": '',
                        "last_name": '',
                    },
                ]
            }
        ]
        self.assertEqual(expected_data, serializer_data)


class ReviewSerializerTestCase(TestCase):
    def test_ok(self):
        self.user1 = User.objects.create(username='test_username1', first_name='petr', last_name='letor')
        self.user2 = User.objects.create(username='test_username2', first_name='metr', last_name='heiter')
        self.user3 = User.objects.create(username='test_username3', )
        review_1 = Review.objects.create(title="Some title", text="text", author_name='jhon', owner=self.user1)
        review_2 = Review.objects.create(title="Some book", text="text", author_name='lemon')

        UserReviewRelation.objects.create(user=self.user1, review=review_1, like=True, rate=3)
        UserReviewRelation.objects.create(user=self.user2, review=review_1, like=True, rate=3)
        ur3 = UserReviewRelation.objects.create(user=self.user3, review=review_1, like=True)
        ur3.rate = 3
        ur3.save()

        UserReviewRelation.objects.create(user=self.user1, review=review_2, like=True, rate=5)
        UserReviewRelation.objects.create(user=self.user2, review=review_2, like=True, rate=2)
        UserReviewRelation.objects.create(user=self.user3, review=review_2, like=False)

        reviews = Review.objects.all().annotate(
            annotated_likes=Count(Case(When(review_with_user__like=True, then=1))),
        ).order_by('id')

        serializer_data = ReviewSerializer(reviews, many=True).data
        expected_data = [
            {
                'id': review_1.id,
                'title': 'Some title',
                'text': 'text',
                'author_name': 'jhon',
                'annotated_likes': 3,
                'rating': '3.00',
                'owner_name': 'test_username1',
                'readers': [
                    {
                        "first_name": 'petr',
                        "last_name": 'letor',
                    },
                    {
                        "first_name": 'metr',
                        "last_name": 'heiter',
                    },
                    {
                        "first_name": '',
                        "last_name": '',
                    },
                ]
            },
            {
                'id': review_2.id,
                'title': 'Some book',
                'text': 'text',
                'author_name': 'lemon',
                'annotated_likes': 2,
                'rating': '3.50',
                "owner_name": '',
                'readers': [
                    {
                        "first_name": 'petr',
                        "last_name": 'letor',
                    },
                    {
                        "first_name": 'metr',
                        "last_name": 'heiter',
                    },
                    {
                        "first_name": '',
                        "last_name": '',
                    },
                ]
            }
        ]
        self.assertEqual(expected_data, serializer_data)


class ArticleSerializerTestCase(TestCase):
    def test_ok(self):
        self.user1 = User.objects.create(username='test_username1', first_name='petr', last_name='letor')
        self.user2 = User.objects.create(username='test_username2', first_name='metr', last_name='heiter')
        self.user3 = User.objects.create(username='test_username3', )
        self.article_1 = Article.objects.create(title="Some title", author_name='jhon', owner=self.user1)
        self.article_2 = Article.objects.create(title="Some book", author_name='lemon')

        UserArticleRelation.objects.create(user=self.user1, article=self.article_1, like=True, rate=3)
        UserArticleRelation.objects.create(user=self.user2, article=self.article_1, like=True, rate=3)
        ur3 = UserArticleRelation.objects.create(user=self.user3, article=self.article_1, like=True)
        ur3.rate = 3
        ur3.save()

        UserArticleRelation.objects.create(user=self.user1, article=self.article_2, like=True, rate=5)
        UserArticleRelation.objects.create(user=self.user2, article=self.article_2, like=True, rate=2)
        UserArticleRelation.objects.create(user=self.user3, article=self.article_2, like=False)

        articles = Article.objects.all().annotate(
            annotated_likes=Count(Case(When(article_with_user__like=True, then=1))),
        ).order_by('id')

        serializer_data = ArticleSerializer(articles, many=True).data
        expected_data = [
            {
                'id': self.article_1.id,
                'title': 'Some title',
                'author_name': 'jhon',
                'annotated_likes': 3,
                'rating': '3.00',
                'owner_name': 'test_username1',

                'readers': [
                    {
                        "first_name": 'petr',
                        "last_name": 'letor',
                    },
                    {
                        "first_name": 'metr',
                        "last_name": 'heiter',
                    },
                    {
                        "first_name": '',
                        "last_name": '',
                    },
                ],
                'date_of_creating': self.article_1.date_of_creating.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
                'date_of_last_update': self.article_1.date_of_last_update.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
            },
            {
                'id': self.article_2.id,
                'title': 'Some book',
                'author_name': 'lemon',
                'annotated_likes': 2,
                'rating': '3.50',
                "owner_name": '',
                'readers': [
                    {
                        "first_name": 'petr',
                        "last_name": 'letor',
                    },
                    {
                        "first_name": 'metr',
                        "last_name": 'heiter',
                    },
                    {
                        "first_name": '',
                        "last_name": '',
                    },
                ],
                'date_of_creating': self.article_2.date_of_creating.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
                'date_of_last_update': self.article_2.date_of_last_update.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
            }
        ]
        print(expected_data)
        print("_____________________________")
        print(serializer_data)
        self.assertEqual(expected_data, serializer_data)
