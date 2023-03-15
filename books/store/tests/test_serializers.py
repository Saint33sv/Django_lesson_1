from django.test import TestCase
from django.contrib.auth.models import User
from django.db.models import Count, Case, When, Max, Min, F
from store.serializers import BookSerializer
from store.models import Book, UserBookRelation, Comments


class BookSerializerTestCase(TestCase):
    def test_ok(self):
        user_1 = User.objects.create(username='user1', first_name='Ivan',
                                     last_name='Ivanov')
        user_2 = User.objects.create(username='user2', first_name='Vitaliy',
                                     last_name='Petrov')
        user_3 = User.objects.create(username='user3', first_name='Kolya',
                                     last_name='Koo')

        book_1 = Book.objects.create(name='Test book 1', price=25,
                                     author_name="Author1", owner=user_1)
        book_2 = Book.objects.create(name='Test book 2', price=55,
                                     author_name="Author2")

        UserBookRelation.objects.create(user=user_1, book=book_1, like=True, 
                                        rate=5) 
        UserBookRelation.objects.create(user=user_2, book=book_1, like=True, 
                                        rate=5)
        user_book3 = UserBookRelation.objects.create(user=user_3, book=book_1, 
                                                    like=True)
        user_book3.rate = 4
        user_book3.save()

        UserBookRelation.objects.create(user=user_1, book=book_2, like=True, 
                                        rate=4)
        UserBookRelation.objects.create(user=user_2, book=book_2, like=True, 
                                        rate=3)
        UserBookRelation.objects.create(user=user_3, book=book_2, like=False)

        Comments.objects.create(user=user_1, book=book_1, text_comment='Good book!')
        Comments.objects.create(user=user_2, book=book_1, 
                                text_comment='Very good book!')

        books = Book.objects.all().annotate(
                annotated_likes=Count(Case(When(userbookrelation__like=True, then=1))),
                max_rating=Max('userbookrelation__rate'),
                min_rating=Min('userbookrelation__rate'),
                owner_name=F('owner__username')
                ).order_by('id')
        data = BookSerializer(books, many=True).data 
        expected_data = [
                {
                    'id': book_1.id,
                    'name': 'Test book 1',
                    'price': '25.00',
                    'author_name':"Author1",
                    'annotated_likes': 3,
                    'rating': '4.67',
                    'max_rating': 5,
                    'min_rating': 4,
                    'owner_name': 'user1',
                    'readers': [
                        {
                            'first_name': 'Ivan',
                            'last_name': 'Ivanov'
                            },
                        {
                            'first_name': 'Vitaliy',
                            'last_name': 'Petrov'
                            },
                        {
                            'first_name': 'Kolya',
                            'last_name': 'Koo'
                            }
                        ]
                    },
                {
                    'id': book_2.id,
                    'name': 'Test book 2',
                    'price': '55.00',
                    'author_name':"Author2",
                    'annotated_likes': 2,
                    'rating': '3.50',
                    'max_rating': 4,
                    'min_rating': 3,
                    'owner_name': None,
                    'readers': [
                        {
                            'first_name': 'Ivan',
                            'last_name': 'Ivanov'
                            },
                        {
                            'first_name': 'Vitaliy',
                            'last_name': 'Petrov'
                            },
                        {
                            'first_name': 'Kolya',
                            'last_name': 'Koo'
                            }
                        ]
                    }
                ]
        self.assertEqual(expected_data, data)
