from django.urls import reverse
from django.contrib.auth.models import User
from django.db import connection
from django.db.models import Count, Case, When, Max, Min, F
from django.utils import timezone
from django.test.utils import CaptureQueriesContext
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from store.models import Book, UserBookRelation, Comments
from store.serializers import BookSerializer
import json


class BooksApiTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username='test_username')
        self.book_1 = Book.objects.create(name='Test book 1', price=25, 
                                        author_name='Author 1',
                                        owner=self.user)
        self.book_2 = Book.objects.create(name='Test book 2', price=55,
                                        author_name='Author 5') 
        self.book_3 = Book.objects.create(name='Test book Author 1', price=60,
                                        author_name='Author 2')
        self.book_4 = Book.objects.create(name='Test book 3', price=100,
                                        author_name='Author 3',
                                        owner=self.user)
        UserBookRelation.objects.create(user=self.user, book=self.book_1, like=True, 
                                        rate=5) 

    def test_get(self):
        url = reverse('book-list') 
        with CaptureQueriesContext(connection) as queries:
            response = self.client.get(url)
            self.assertEqual(2, len(queries))
        books = Book.objects.all().annotate(
                annotated_likes=Count(Case(When(userbookrelation__like=True, then=1))),
                max_rating=Max('userbookrelation__rate'),
                min_rating=Min('userbookrelation__rate'),
                count_comments=Count('comments__text_comment'),
                owner_name=F('owner__username')
                ).order_by('id')
        serializer_data = BookSerializer(books, many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)
        self.assertEqual(serializer_data[0]['rating'], '5.00')
        self.assertEqual(serializer_data[0]['annotated_likes'], 1)

    def test_filter(self):
        url = reverse('book-list') 
        response = self.client.get(url, data={'price': 55})
        books = Book.objects.filter(id__in=[self.book_2.id,]).annotate(
                annotated_likes=Count(Case(When(userbookrelation__like=True, then=1))),
                max_rating=Max('userbookrelation__rate'),
                min_rating=Min('userbookrelation__rate'),
                count_comments=Count('comments__text_comment'),
                owner_name=F('owner__username')
                ).order_by('id')
        serializer_data = BookSerializer(books, many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_search(self):
        url = reverse('book-list') 
        response = self.client.get(url, data={'search': 'Author 1'})
        books = Book.objects.filter(id__in=[self.book_1.id, self.book_3.id]).annotate(
                annotated_likes=Count(Case(When(userbookrelation__like=True, then=1))),
                max_rating=Max('userbookrelation__rate'),
                min_rating=Min('userbookrelation__rate'),
                count_comments=Count('comments__text_comment'),
                owner_name=F('owner__username')
                ).order_by('id')
        serializer_data = BookSerializer(books, many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_ordering(self):
        url = reverse('book-list') 
        response = self.client.get(url, data={'ordering': 'price'})
        books = Book.objects.all().annotate(
                annotated_likes=Count(Case(When(userbookrelation__like=True, then=1))),
                max_rating=Max('userbookrelation__rate'),
                min_rating=Min('userbookrelation__rate'),
                count_comments=Count('comments__text_comment'),
                owner_name=F('owner__username')
                ).order_by('price')
        serializer_data = BookSerializer(books, many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_create(self):
        self.assertEqual(4, Book.objects.all().count()) 
        url = reverse('book-list') 
        data = {"name": "Programming in Python 3",
                "price": 150,
                "author_name": "Mark Summerfield"
               }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.post(url, data=json_data, 
                                    content_type='application/json') 
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(5, Book.objects.all().count())
        self.assertEqual(Book.objects.last().name, data['name'])
        self.assertEqual(str(Book.objects.last().price), '150.00')
        self.assertEqual(Book.objects.last().author_name, data['author_name'])
        self.assertEqual(self.user, Book.objects.last().owner)

    def test_update(self): 
        url = reverse('book-detail', args=(self.book_1.id,)) 
        data = {"name": self.book_1.name,
                "price": 575,
                "author_name": self.book_1.author_name
               }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.put(url, data=json_data, 
                                    content_type='application/json') 
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.book_1.refresh_from_db()
        self.assertEqual(575, self.book_1.price)
    
    def test_delete(self):
        self.assertEqual(4, Book.objects.all().count()) 
        url = reverse('book-detail', args=(self.book_4.id,)) 
        self.client.force_login(self.user)
        response = self.client.delete(url, data=self.book_4.id, 
                                    content_type='application/json') 
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
        self.assertEqual(3, Book.objects.all().count())
        response_2 = self.client.get(url)
        self.assertEqual(status.HTTP_404_NOT_FOUND, response_2.status_code)

    def test_get_one_object(self):
       url = reverse('book-detail', args=(self.book_2.id,)) 
       response = self.client.get(url)
       expected_data = {'id': 19, 'name': 'Test book 2', 
                        'price': '55.00', 
                        'author_name': 'Author 5', 
                        'annotated_likes': 0,
                        'rating': None,
                        'max_rating': None,
                        'min_rating': None,
                        'count_comments': 0,
                        'owner_name': None,
                        'readers': []
                        }

       self.assertEqual(status.HTTP_200_OK, response.status_code)
       self.assertEqual(expected_data, response.data)

    def test_update_not_owner(self):
        self.user2 = User.objects.create(username='test_username2')
        url = reverse('book-detail', args=(self.book_1.id,)) 
        data = {"name": self.book_1.name,
                "price": 575,
                "author_name": self.book_1.author_name
               }
        json_data = json.dumps(data)
        self.client.force_login(self.user2)
        response = self.client.put(url, data=json_data, 
                                    content_type='application/json') 
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
        self.assertEqual({'detail': ErrorDetail
                        (string='You do not have permission to perform this action.', 
                         code='permission_denied')}, response.data)
        self.book_1.refresh_from_db()
        self.assertEqual(25, self.book_1.price)

    def test_update_not_owner_but_staff(self):
        self.user2 = User.objects.create(username='test_username2',
                                         is_staff=True)
        url = reverse('book-detail', args=(self.book_1.id,)) 
        data = {"name": self.book_1.name,
                "price": 575,
                "author_name": self.book_1.author_name
               }
        json_data = json.dumps(data)
        self.client.force_login(self.user2)
        response = self.client.put(url, data=json_data, 
                                    content_type='application/json') 
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.book_1.refresh_from_db()
        self.assertEqual(575, self.book_1.price)


class BooksRelationTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username='test_username')
        self.user2 = User.objects.create(username='test_username2')
        self.book_1 = Book.objects.create(name='Test book 1', price=25, 
                                        author_name='Author 1',
                                        owner=self.user)
        self.book_2 = Book.objects.create(name='Test book 2', price=55,
                                        author_name='Author 5') 

    def test_like(self):
        url = reverse('userbookrelation-detail', args=(self.book_1.id,)) 
        data = {
                "like": True
               }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.patch(url, data=json_data,
                                     content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        relation = UserBookRelation.objects.get(user=self.user,
                                                book=self.book_1)
        self.assertTrue(relation.like)
        data = {
                "in_bookmarks": True
               }
        json_data = json.dumps(data)
        response = self.client.patch(url, data=json_data,
                                     content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        
        relation = UserBookRelation.objects.get(user=self.user,
                                                book=self.book_1)
        self.assertTrue(relation.in_bookmarks)

    def test_rate(self):
        url = reverse('userbookrelation-detail', args=(self.book_1.id,)) 
        data = {
                "rate": 3
               }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.patch(url, data=json_data,
                                     content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        relation = UserBookRelation.objects.get(user=self.user,
                                                book=self.book_1)
        self.assertEqual(3, relation.rate)
        
    def test_rate_wrong(self):
        url = reverse('userbookrelation-detail', args=(self.book_1.id,)) 
        data = {
                "rate": 6
               }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.patch(url, data=json_data,
                                     content_type='application/json')
        self.assertEqual(status.HTTP_400_BAD_REQUEST, 
                         response.status_code, response.data)
        relation = UserBookRelation.objects.get(user=self.user,
                                                book=self.book_1)
        self.assertEqual(None, relation.rate)
        
    def test_comment(self):
        url = reverse('userbookrelation-detail', args=(self.book_2.id,)) 
        data = {
                "comment": 'Very good book!'
               }
        json_data = json.dumps(data)
        self.client.force_login(self.user2)
        response = self.client.patch(url, data=json_data,
                                     content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        relation = UserBookRelation.objects.get(user=self.user2,
                                                book=self.book_2)
        self.assertEqual('Very good book!', relation.comment)
 

class CommentsTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username='test_username')
        self.user2 = User.objects.create(username='test_username2')
        self.book_1 = Book.objects.create(name='Test book 1', price=25, 
                                        author_name='Author 1',
                                        owner=self.user)
        self.book_2 = Book.objects.create(name='Test book 2', price=55,
                                        author_name='Author 5') 

    def test_comment(self):
        url = reverse('comments-detail', args=(self.book_1.id,)) 
        data = {
                "text_comment": 'Good book!'
               }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.patch(url, data=json_data,
                                     content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        comment = Comments.objects.get(user=self.user,
                                                book=self.book_1)
        self.assertEqual('Good book!', comment.text_comment)
        
    def test_comment_date(self):
        url = reverse('comments-detail', args=(self.book_1.id,)) 
        data = {
                "text_comment": 'Good book!'
               }
        json_data = json.dumps(data)
        self.client.force_login(self.user2)
        response = self.client.patch(url, data=json_data,
                                     content_type='application/json')
        
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        comment = Comments.objects.get(user=self.user2,
                                                book=self.book_1)
        self.assertEqual(timezone.now().strftime('%d.%m.%Y %H:%M'), 
                         comment.comment_date.strftime('%d.%m.%Y %H:%M'))
        
    def test_comment_count(self):
        url = reverse('comments-detail', args=(self.book_1.id,)) 
        data = {
                "text_comment": 'Good book!'
               }
        json_data = json.dumps(data)
        self.client.force_login(self.user2)
        response = self.client.patch(url, data=json_data,
                                     content_type='application/json')
        
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        comment_count = Comments.objects.filter(book=self.book_1).count()
        self.assertEqual(1, comment_count)

        self.client.force_login(self.user)
        response = self.client.patch(url, data=json_data,
                                     content_type='application/json')
        
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        comment_count = Comments.objects.filter(book=self.book_1).count()
        self.assertEqual(2, comment_count)
