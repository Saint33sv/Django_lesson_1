# Generated by Django 4.1.6 on 2023-03-06 14:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0007_userbookrelation_comment'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userbookrelation',
            name='comment',
        ),
    ]
