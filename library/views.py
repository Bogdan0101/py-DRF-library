from rest_framework import viewsets, mixins
from rest_framework.viewsets import GenericViewSet
from library.permissions import IsAdminOrAllReadOnly

from library.serializers import (
    BookSerializer,
    BorrowingSerializer,
    BorrowingListSerializer,
    BorrowingDetailSerializer,
    BorrowingCreateSerializer,
    BorrowingUpdateSerializer,
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
        is_active = self.request.GET.get("is_active")
        if is_active is not None:
            is_active = is_active.lower() == "true"
            queryset = queryset.filter(is_active=is_active)

        if self.request.user.is_superuser:
            id_user = self.request.GET.get("id_user")
            if id_user:
                queryset = queryset.filter(user__id=id_user)
            return queryset.distinct()

        queryset = queryset.filter(user=self.request.user)
        return queryset.distinct()

    def get_serializer_class(self):
        if self.action == "list":
            return BorrowingListSerializer
        if self.action == "retrieve":
            return BorrowingDetailSerializer
        if self.action == "create":
            return BorrowingCreateSerializer
        if self.action in ("update", "partial_update"):
            return BorrowingUpdateSerializer
        return BorrowingSerializer
