from rest_framework import serializers
from library.models import (
    Book,
    Borrowing,
)


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ("id", "title", "author", "cover", "inventory", "daily_fee")


class BookTitleSerializer(BookSerializer):
    class Meta:
        model = Book
        fields = ("title", "daily_fee")


class BorrowingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = ("id", "borrow_date", "actual_return_date", "expected_return_date", "book", "user")
        read_only_fields = ("id", "borrow_date", "actual_return_date", "user")


class BorrowingListSerializer(BorrowingSerializer):
    book = BookTitleSerializer()


class BorrowingDetailSerializer(BorrowingSerializer):
    book = BookTitleSerializer()
    user = serializers.CharField(source="user.email", read_only=True)

    class Meta:
        model = Borrowing
        fields = ("id", "borrow_date", "actual_return_date", "expected_return_date", "book", "user")
        read_only_fields = ("id", "borrow_date", "actual_return_date", "user")
