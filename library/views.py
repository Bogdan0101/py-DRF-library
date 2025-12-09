from rest_framework import viewsets
from library.serializers import BookSerializer
from library.models import Book


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all().order_by("id")
    serializer_class = BookSerializer
