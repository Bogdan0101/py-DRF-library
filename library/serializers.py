from rest_framework import serializers
from library.telegram import send_telegram_message
from library.models import (
    Book,
    Borrowing, Payment,
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
        fields = ("id",
                  "borrow_date",
                  "actual_return_date",
                  "expected_return_date",
                  "is_active",
                  "book",
                  "user")
        read_only_fields = ("id", "user", "is_active",)

    def create(self, validated_data):
        book = validated_data["book"]
        if book.inventory <= 0:
            raise (serializers
                   .ValidationError("Inventory must be greater than 0"))
        book.borrow()
        borrowing = Borrowing.objects.create(
            **validated_data,
            user=self.context["request"].user,
        )
        message = (f"New borrowing: '{book.title}', "
                   f"User: {borrowing.user.email}, "
                   f"Expected: {borrowing.expected_return_date}")
        send_telegram_message(message)
        return borrowing

    def update(self, instance, validated_data):
        old_return_date = instance.actual_return_date
        new_return_date = validated_data.get("actual_return_date")
        instance.actual_return_date = new_return_date
        if old_return_date is None and new_return_date is not None:
            instance.is_active = False
            instance.book.return_book()
        instance.save()
        return instance


class BorrowingCreateSerializer(BorrowingSerializer):
    class Meta:
        model = Borrowing
        fields = ("id",
                  "borrow_date",
                  "actual_return_date",
                  "expected_return_date",
                  "book",
                  "user")
        read_only_fields = ("id", "borrow_date", "actual_return_date", "user")


class BorrowingUpdateSerializer(BorrowingSerializer):
    class Meta:
        model = Borrowing
        fields = ("id",
                  "borrow_date",
                  "actual_return_date",
                  "expected_return_date",
                  "book",
                  "user")
        read_only_fields = ("id",
                            "borrow_date",
                            "expected_return_date",
                            "user",
                            "book")


class BorrowingListSerializer(BorrowingSerializer):
    book = BookTitleSerializer()

    class Meta:
        model = Borrowing
        fields = ("id",
                  "borrow_date",
                  "actual_return_date",
                  "expected_return_date",
                  "is_active",
                  "book",
                  "user")


class BorrowingDetailSerializer(BorrowingSerializer):
    book = BookTitleSerializer()
    user = serializers.CharField(source="user.email", read_only=True)

    class Meta:
        model = Borrowing
        fields = ("id",
                  "borrow_date",
                  "actual_return_date",
                  "expected_return_date",
                  "is_active",
                  "book",
                  "user")


class PaymentSerializer(serializers.ModelSerializer):
    borrowing = BorrowingDetailSerializer()

    class Meta:
        model = Payment
        fields = ("id",
                  "status",
                  "type_transaction",
                  "borrowing",
                  "session_url",
                  "session_id"
                  )
