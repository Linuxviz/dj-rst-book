from django.contrib.auth.models import User
from django.test import TestCase

from store.logic import set_rating
from store.models import Book, UserBookRelation, Article, UserArticleRelation


class SetRatingTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create(username='test_username1', first_name='petr', last_name='letor')
        self.user2 = User.objects.create(username='test_username2', first_name='metr', last_name='heiter')
        self.user3 = User.objects.create(username='test_username3', )

        self.book_1 = Book.objects.create(title="Some title", price='2500.00', author_name='jhon', owner=self.user1)

        ur1 = UserBookRelation.objects.create(user=self.user1, book=self.book_1, like=True, rate=3)
        ur2 = UserBookRelation.objects.create(user=self.user2, book=self.book_1, like=True, rate=4)
        ur3 = UserBookRelation.objects.create(user=self.user3, book=self.book_1, like=True, rate=5)

        self.article_1 = Article.objects.create(title='title_art_1', author_name='auth_name_1', owner=self.user1)
        self.userArticle = UserArticleRelation.objects.create(user=self.user2, article=self.article_1, like=True, rate=3)

    def test_ok(self):
        set_rating(self.book_1, UserBookRelation, "book")
        self.book_1.refresh_from_db()
        self.assertEqual(self.book_1.rating, 4.0, "рейтинг обновился по-другому")
        set_rating(self.article_1, UserArticleRelation, "article")
        self.article_1.refresh_from_db()
        self.assertEqual(self.article_1.rating, 3.0, "рейтинг обновился по-другому")
