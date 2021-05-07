from django.contrib import auth
from django.contrib.auth.models import User
from django.test import TestCase

from store.models import Article, UserArticleRelation


class ArticleModelTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create(username='test_username1', first_name='petr', last_name='letor')
        self.user2 = User.objects.create(username='test_username2', first_name='petr1', last_name='letor1')
        self.article1 = Article.objects.create(title='title_art_1', author_name='auth_name_1', owner=self.user1)
        self.userArticle = UserArticleRelation.objects.create(user=self.user2, article=self.article1, like=True, rate=3)

    def test_get(self):
        x = Article.objects.get(pk=self.article1.pk)
        data = (
                x.title,
                x.author_name,
                x.owner.username,
                list(x.readers.all()),
                x.rating,
                x.date_of_creating,
                x.date_of_last_update,
        )
        expected_data = (
                'title_art_1',
                'auth_name_1',
                'test_username1',
                [self.user2],
                3.00,
                x.date_of_creating,
                x.date_of_last_update,
        )
        self.assertEqual(expected_data, data, "изменились поля модели")
