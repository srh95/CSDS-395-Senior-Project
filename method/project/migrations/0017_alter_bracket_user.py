# Generated by Django 3.2.9 on 2021-11-26 00:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0016_alter_user_favbracket'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bracket',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='project.user'),
        ),
    ]