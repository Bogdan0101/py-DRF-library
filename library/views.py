from rest_framework import viewsets, mixins
from rest_framework.viewsets import GenericViewSet

from library.serializers import (
    BookSerializer,
    BorrowingSerializer,
    BorrowingListSerializer,
    BorrowingDetailSerializer,
)
from library.models import (
    Book,
    Borrowing,
)


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all().order_by("id")
    serializer_class = BookSerializer


class BorrowingViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    GenericViewSet,
):
    queryset = (Borrowing.objects.all()
                .order_by("id")
                .select_related("book", "user"))
    serializer_class = BorrowingSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return BorrowingListSerializer
        if self.action == "retrieve":
            return BorrowingDetailSerializer
        return BorrowingSerializer
