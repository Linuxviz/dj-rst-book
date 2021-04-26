from django.shortcuts import render

# Create your views here.
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from store.models import Book
from store.serializer import BooksSerializer


class BookViewSet(ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BooksSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filter_fields = ['price']  # фильтр сортирует конкретное поле по знаению
    search_fields = ['title', 'author_name']  # поиск позволяет искать все совпадения в указанных полях
    ordering_fields = ['price', 'author_name']
    permission_classes = [IsAuthenticated]
