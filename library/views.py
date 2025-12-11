from rest_framework import viewsets, mixins
from rest_framework.viewsets import GenericViewSet
from library.permissions import IsAdminOrAllReadOnly

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
    permission_classes = (IsAdminOrAllReadOnly,)


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

    def get_queryset(self):
        queryset = self.queryset
        if not self.request.user.is_superuser:
            queryset = queryset.filter(user=self.request.user)
        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return BorrowingListSerializer
        if self.action == "retrieve":
            return BorrowingDetailSerializer
        return BorrowingSerializer
