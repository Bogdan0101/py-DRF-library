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

    def create(self, validated_data):
        book = validated_data["book"]
        if book.inventory <= 0:
            raise serializers.ValidationError("Inventory must be greater than 0")
        book.borrow()
        borrowing = Borrowing.objects.create(
            **validated_data,
            user=self.context["request"].user,
        )
        return borrowing

    def update(self, instance, validated_data):
        old_return_date = instance.actual_return_date
        new_return_date = validated_data.get("actual_return_date")
        instance.actual_return_date = new_return_date
        instance.save()
        if old_return_date is None and new_return_date is not None:
            instance.book.return_book()
        return instance


class BorrowingListSerializer(BorrowingSerializer):
    book = BookTitleSerializer()


class BorrowingDetailSerializer(BorrowingSerializer):
    book = BookTitleSerializer()
    user = serializers.CharField(source="user.email", read_only=True)

    class Meta:
        model = Borrowing
        fields = ("id", "borrow_date", "actual_return_date", "expected_return_date", "book", "user")
        read_only_fields = ("id", "borrow_date", "actual_return_date", "user")
