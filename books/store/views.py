from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Case, When, Max, Min, F
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.mixins import UpdateModelMixin
from rest_framework.permissions import IsAuthenticated
from store.models import Book, UserBookRelation, Comments
from store.serializers import BookSerializer, UserBookRelationSerializer, CommentsSerializer
from store.permissions import IsOwnerOrStaffOrReadOnly


class BookViewSet(ModelViewSet):
    queryset = Book.objects.all().annotate(
                annotated_likes=Count(Case(When(userbookrelation__like=True, then=1))),
                max_rating=Max('userbookrelation__rate'),
                min_rating=Min('userbookrelation__rate'),
                count_comments=Count('comments__text_comment'),
                owner_name = F('owner__username')
                ).prefetch_related('readers').order_by('id')
    serializer_class = BookSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    permission_classes = [IsOwnerOrStaffOrReadOnly]
    filterset_fields = ['price']
    search_fields = ['name', 'author_name']
    ordering_fields = ['price', 'author_name']

    def perform_create(self, serializer):
        serializer.validated_data['owner'] = self.request.user
        serializer.save()


class UserBooksRelationView(UpdateModelMixin, GenericViewSet):
    permission_classes = [IsAuthenticated] # права доступа
    queryset = UserBookRelation.objects.all() # набор запросов
    serializer_class = UserBookRelationSerializer
    lookup_field = 'book'

    def get_object(self):
        obj, _ = UserBookRelation.objects.get_or_create(user=self.request.user,
                                                        book_id=self.kwargs['book'])
        return obj


class CommentsView(UpdateModelMixin, GenericViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Comments.objects.all()
    serializer_class = CommentsSerializer
    lookup_field = 'book'

    def get_object(self):
        obj, _ = Comments.objects.get_or_create(user=self.request.user,
                                                book_id=self.kwargs['book'])
        return obj

def oauth(request):
    return render(request, 'oauth.html')
