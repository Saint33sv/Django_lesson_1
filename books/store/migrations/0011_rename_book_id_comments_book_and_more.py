# Generated by Django 4.1.6 on 2023-03-06 16:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0010_comments'),
    ]

    operations = [
        migrations.RenameField(
            model_name='comments',
            old_name='book_id',
            new_name='book',
        ),
        migrations.RenameField(
            model_name='comments',
            old_name='user_id',
            new_name='user',
        ),
    ]
