# Generated by Django 3.2 on 2021-05-07 10:45

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('store', '0008_book_rating'),
    ]

    operations = [
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('author_name', models.CharField(max_length=255)),
                ('rating', models.DecimalField(decimal_places=2, default=None, max_digits=3, null=True)),
                ('date_of_creating', models.DateTimeField(auto_now_add=True)),
                ('date_of_last_update', models.DateTimeField(auto_now=True)),
                ('owner', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='articles', to=settings.AUTH_USER_MODEL)),
                ('readers', models.ManyToManyField(related_name='readed_articles', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
