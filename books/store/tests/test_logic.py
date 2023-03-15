from django.test import TestCase
from django.contrib.auth.models import User

from store.logic import set_rating
from store.models import Book, UserBookRelation


class SetRatingTestCase(TestCase):
    def setUp(self):
        self.user_1 = User.objects.create(username='user1', first_name='Ivan',
                                     last_name='Ivanov')
        self.user_2 = User.objects.create(username='user2', first_name='Vitaliy',
                                     last_name='Petrov')
        self.user_3 = User.objects.create(username='user3', first_name='Kolya',
                                     last_name='Koo')

        self.book_1 = Book.objects.create(name='Test book 1', price=25,
                                     author_name="Author1", owner=self.user_1)

        UserBookRelation.objects.create(user=self.user_1, book=self.book_1, like=True, 
                                        rate=5) 
        UserBookRelation.objects.create(user=self.user_2, book=self.book_1, like=True, 
                                        rate=5)
        UserBookRelation.objects.create(user=self.user_3, book=self.book_1, like=True,
                                        rate=4)
    def test_ok(self):
        set_rating(self.book_1)
        self.book_1.refresh_from_db()
        self.assertEqual('4.67', str(self.book_1.rating))

    def test_update(self):
        user_book = UserBookRelation.objects.create(user=self.user_3, book=self.book_1)
        user_book.rate = 5
        user_book.old_rate = user_book.rate
        user_book.save()
        self.assertEqual('4.666666666666667', str(self.book_1.rating))
