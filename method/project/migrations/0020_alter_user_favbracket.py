# Generated by Django 3.2.9 on 2021-11-28 03:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0019_merge_20211127_2028'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='favbracket',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='project.bracket'),
        ),
    ]
