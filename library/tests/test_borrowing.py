from datetime import timedelta, date
from unittest.mock import patch
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status
from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse
from library.models import Borrowing, Book
from library.serializers import BorrowingListSerializer

BORROWING_URL = reverse("library:borrowings-list")


class AdminBorrowingTests(TestCase):
    def setUp(self):
        self.patcher = patch("library.serializers.send_telegram_message")
        self.mock_telegram = self.patcher.start()
        self.patcher_stripe = patch("library.payments.stripe.stripe.checkout.Session.create")
        self.mock_stripe = self.patcher_stripe.start()

        self.mock_stripe.return_value = type("obj", (object,), {
            "id": "test_session_id",
            "url": "http://test-url.com",
        })
        self.addCleanup(self.patcher_stripe.stop)

        self.addCleanup(self.patcher.stop)

        cache.clear()
        self.admin = get_user_model().objects.create_superuser(
            email="admin@gmail.com",
            first_name="admin",
            last_name="admin",
            password="ASDFfasf123!@#",
        )
        self.user = get_user_model().objects.create_user(
            email="user@gmail.com",
            first_name="user",
            last_name="user",
            password="ASDasfsfgwe$123",
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.admin)
        self.book1 = Book.objects.create(
            title="Book JS",
            author="John Black",
            cover="HARD",
            inventory=3,
            daily_fee=3.20,
        )
        self.book2 = Book.objects.create(
            title="Book PHP",
            author="Bob Black",
            cover="HARD",
            inventory=5,
            daily_fee=2.20,
        )
        self.borrowing1 = Borrowing.objects.create(
            user=self.admin,
            book=self.book1,
            expected_return_date=date.today() + timedelta(days=3),
        )
        self.borrowing2 = Borrowing.objects.create(
            user=self.user,
            book=self.book2,
            expected_return_date=date.today() + timedelta(days=4),
        )
        self.borrowing2_ser = BorrowingListSerializer(self.borrowing2).data
        self.borrowings_ser = BorrowingListSerializer([self.borrowing1, self.borrowing2], many=True).data

    def test_str(self):
        self.assertEqual(str(self.borrowing2), f"{self.borrowing2.book.title}, {self.borrowing2.borrow_date}")

    def test_total_amount_cents(self):
        self.assertEqual(self.borrowing2.total_amount_cents(), 880)
        self.borrowing2.expected_return_date = date.today()
        self.assertEqual(self.borrowing2.total_amount_cents(), 220)

    def test_filter_user_id_for_admin(self):
        data = {
            "id_user": self.user.id,
        }
        res = self.client.get(BORROWING_URL, data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data["results"]), 1)
        self.assertEqual(res.data["results"][0], self.borrowing2_ser)

    def test_filter_is_active_for_admin(self):
        data = {
            "is_active": True,
        }
        res = self.client.get(BORROWING_URL, data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data["results"]), 2)
        self.assertEqual(res.data["results"], self.borrowings_ser)

    def test_get_and_can_see_all_borrowing_for_admin(self):
        res = self.client.get(BORROWING_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data["results"]), 2)
        self.assertEqual(res.data["results"], self.borrowings_ser)

    def test_post_for_admin(self):
        data = {
            "book": self.book1.id,
            "expected_return_date": date.today() + timedelta(days=3),
        }
        res = self.client.post(BORROWING_URL, data)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        borrowing = Borrowing.objects.filter(**data).first()
        self.assertIsNotNone(borrowing)
        self.assertEqual(borrowing.borrow_date, timezone.now().date())
        self.mock_telegram.assert_called_once()


class UserAuthBorrowingTests(TestCase):
    def setUp(self):
        self.patcher = patch("library.serializers.send_telegram_message")
        self.mock_telegram = self.patcher.start()
        self.patcher_stripe = patch("library.payments.stripe.stripe.checkout.Session.create")
        self.mock_stripe = self.patcher_stripe.start()

        self.mock_stripe.return_value = type("obj", (object,), {
            "id": "test_session_id",
            "url": "http://test-url.com",
        })
        self.addCleanup(self.patcher_stripe.stop)
        self.addCleanup(self.patcher.stop)

        cache.clear()
        self.admin = get_user_model().objects.create_superuser(
            email="admin@gmail.com",
            first_name="admin",
            last_name="admin",
            password="ASDFfasf123!@#",
        )
        self.user = get_user_model().objects.create_user(
            email="user@gmail.com",
            first_name="user",
            last_name="user",
            password="ASDasfsfgwe$123",
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.book1 = Book.objects.create(
            title="Book JS",
            author="John Black",
            cover="HARD",
            inventory=3,
            daily_fee=3.20,
        )
        self.book2 = Book.objects.create(
            title="Book PHP",
            author="Bob Black",
            cover="HARD",
            inventory=5,
            daily_fee=2.20,
        )
        self.borrowing1 = Borrowing.objects.create(
            user=self.admin,
            book=self.book1,
            expected_return_date=date.today() + timedelta(days=3),
        )
        self.borrowing2 = Borrowing.objects.create(
            user=self.user,
            book=self.book2,
            expected_return_date=date.today() + timedelta(days=4),
        )
        self.borrowing2_ser = BorrowingListSerializer(self.borrowing2).data
        self.borrowings_ser = BorrowingListSerializer([self.borrowing1, self.borrowing2], many=True).data

    def test_filter_is_active_for_user(self):
        data = {
            "is_active": False,
        }
        res = self.client.get(BORROWING_URL, data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data["results"]), 0)

    def test_get_and_can_see_only_their_borrowing(self):
        res = self.client.get(BORROWING_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data["results"]), 1)
        self.assertEqual(res.data["results"][0], self.borrowing2_ser)

    def test_post_for_user(self):
        data = {
            "book": self.book1.id,
            "expected_return_date": date.today() + timedelta(days=3),
        }
        res = self.client.post(BORROWING_URL, data)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        borrowing = Borrowing.objects.filter(**data).first()
        self.assertIsNotNone(borrowing)
        self.assertEqual(borrowing.borrow_date, timezone.now().date())
        self.mock_telegram.assert_called_once()


class UnauthenticatedBorrowingTests(TestCase):
    def setUp(self):
        cache.clear()
        self.client = APIClient()

    def test_get_unauthenticated_user(self):
        res = self.client.get(BORROWING_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
