from django.contrib import admin
from django.contrib.admin import ModelAdmin
from .models import Book, UserBookRelation, Comments


@admin.register(Book)
class BookAdmin(ModelAdmin):
    pass


@admin.register(UserBookRelation)
class UserBookRelationAdmin(ModelAdmin):
    pass


@admin.register(Comments)
class COmmentsAdmin(ModelAdmin):
    pass
