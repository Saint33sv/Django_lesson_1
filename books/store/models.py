from django.contrib.auth.models import User
from django.db import models


class Book(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    author_name = models.CharField(max_length=255)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL,
                              null=True, related_name='my_books')
    readers = models.ManyToManyField(User, through='UserBookRelation',
                                      related_name='books')
    commentators = models.ManyToManyField(User, through='Comments',
                                          related_name='book_comment')
    rating = models.DecimalField(max_digits=3, decimal_places=2,
                                 default=None, null=True)


    def __str__(self):
        return f"Id {self.id}: {self.name}"


class UserBookRelation(models.Model):
    RATE_CHOICES = (
            (1, 'Ok'),
            (2, 'Fine'),
            (3, 'Good'),
            (4, 'Amazing'),
            (5, 'Incredibel')
            )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    like = models.BooleanField(default=False)
    in_bookmarks = models.BooleanField(default=False)
    rate = models.SmallIntegerField(choices=RATE_CHOICES, null=True)
    comment = models.TextField(null=True)
    
    def __str__(self):
        return f"{self.user.username}: {self.book.name} RATE {self.rate}"

    def __init__(self, *args, **kwargs):
        super(UserBookRelation, self).__init__(*args, **kwargs)
        self.old_rate = self.rate

    def save(self, *args, **kwargs):
        creating = not self.pk

        super().save(*args, **kwargs)

        if self.old_rate != self.rate or creating:
            from store.logic import set_rating
            set_rating(self.book)


class Comments(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    text_comment = models.TextField(null=True)
    comment_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user}:{self.book.name}.Comment: {self.text_comment[0:20]} {self.comment_date.strftime('%d.%m.%Y %H:%M')}"
