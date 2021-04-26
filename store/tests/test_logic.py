from django.test import TestCase

from store.logic import operations


class LogicTestCase(TestCase):
    def test_plus(self):
        result = operations(5, 3, '+')
        self.assertEqual(8, result)

    def test_minus(self):
        result = operations(5, 3, '-')
        self.assertEqual(2, result)

    def test_multiply(self):
        result = operations(5, 3, '*')
        self.assertEqual(15, result)