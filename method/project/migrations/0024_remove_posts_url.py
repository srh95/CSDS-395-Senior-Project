# Generated by Django 3.2.9 on 2021-11-28 23:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0023_auto_20211128_1645'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='posts',
            name='url',
        ),
    ]
