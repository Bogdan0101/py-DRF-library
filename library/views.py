from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
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
    PaymentSerializer,
)
from library.models import (
    Book,
    Borrowing,
    Payment,
)


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all().order_by("id")
    serializer_class = BookSerializer
    permission_classes = (IsAdminOrAllReadOnly,)

    def get_queryset(self):
        queryset = self.queryset
        title = self.request.GET.get("title")
        if title:
            queryset = queryset.filter(title__icontains=title)
        return queryset.distinct()

    @extend_schema(parameters=[
        OpenApiParameter(
            name="title",
            type=str,
            description="Filter by title (ex. ?title=book)",
        )
    ])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


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

    @extend_schema(parameters=[
        OpenApiParameter(
            name="is_active",
            type=bool,
            description="Filter by is_active (ex. ?is_active=True)",
        ),
        OpenApiParameter(
            name="id_user",
            type=int,
            description="Filter by id_user (ex. ?id_user=2)",
        )
    ])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

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


class PaymentViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet,
):
    queryset = (Payment.objects.all()
                .select_related("borrowing",
                                "borrowing__user",
                                "borrowing__book"
                                ).order_by("id"))
    serializer_class = PaymentSerializer

    def get_queryset(self):
        queryset = self.queryset

        if self.request.user.is_superuser:
            id_user = self.request.GET.get("id_user")
            if id_user:
                queryset = queryset.filter(borrowing__user__id=id_user)
            return queryset.distinct()

        queryset = queryset.filter(borrowing__user=self.request.user)
        return queryset.distinct()

    @extend_schema(parameters=[
        OpenApiParameter(
            name="id_user",
            type=int,
            description="Filter by id_user (ex. ?id_user=2)",
        )
    ])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
