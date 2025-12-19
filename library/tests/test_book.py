from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.core.cache import cache
from library.models import Book
from library.serializers import BookSerializer

BOOK_URL = reverse("library:books-list")


class BookAdminTests(TestCase):
    def setUp(self):
        cache.clear()
        self.admin = get_user_model().objects.create_superuser(
            email="admin@gmail.com",
            first_name="admin",
            last_name="admin",
            password="ASDFfasf123!@#",
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
        self.book3 = Book.objects.create(
            title="Book Python",
            author="Bob Black",
            cover="HARD",
            inventory=2,
            daily_fee=4.20,
        )
        self.book1_serializer = BookSerializer(self.book1).data
        self.books_serializer = BookSerializer([self.book1, self.book2, self.book3], many=True).data

    def test_str_for_book(self):
        self.assertEqual(
            str(self.book1),
            f"{self.book1.title}, {self.book1.author}"
        )

    def test_borrow_for_book_with_positive_inventory(self):
        self.book1.borrow()
        self.assertEqual(2, self.book1.inventory)

    def test_borrow_for_book_with_inventory_null(self):
        self.book3.inventory = 0
        self.book3.save()
        with self.assertRaises(ValueError):
            self.book3.borrow()

    def test_borrow_return_book(self):
        self.book1.inventory = 3
        self.book1.return_book()
        self.assertEqual(4, self.book1.inventory)

    def test_post_admin(self):
        data = {
            "title": "Book",
            "author": "Bob Black",
            "cover": "HARD",
            "inventory": 5,
            "daily_fee": 2.20,
        }
        res = self.client.post(BOOK_URL, data=data)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Book.objects.filter(**data).exists())

    def test_get_admin(self):
        res = self.client.get(BOOK_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(3, len(res.data["results"]))
        self.assertEqual(res.data["results"], self.books_serializer)

    def test_get_with_filter(self):
        data = {"title": self.book1.title}
        res = self.client.get(BOOK_URL, data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data["results"]), 1)
        self.assertEqual(res.data["results"][0], self.book1_serializer)


class BookUserAndUnauthenticateUserTests(TestCase):
    def setUp(self):
        cache.clear()
        self.user = get_user_model().objects.create_user(
            email="user@gmail.com",
            first_name="user",
            last_name="user",
            password="ASDasfsfgwe$123",
        )
        self.client = APIClient()
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
        self.book1_serializer = BookSerializer(self.book1).data
        self.books_serializer = BookSerializer([self.book1, self.book2], many=True).data

    def test_get_authenticate_user(self):
        self.client.force_authenticate(user=self.user)
        res = self.client.get(BOOK_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(2, len(res.data["results"]))
        self.assertEqual(res.data["results"], self.books_serializer)

    def test_get_unauthenticate_user(self):
        res = self.client.get(BOOK_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(2, len(res.data["results"]))
        self.assertEqual(res.data["results"], self.books_serializer)

    def test_post_authenticate_user(self):
        self.client.force_authenticate(user=self.user)
        data = {
            "title": "Book",
            "author": "Bob Black",
            "cover": "HARD",
            "inventory": 5,
            "daily_fee": 2.20,
        }
        res = self.client.post(BOOK_URL, data=data)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_post_unauthenticate_user(self):
        data = {
            "title": "Book",
            "author": "Bob Black",
            "cover": "HARD",
            "inventory": 5,
            "daily_fee": 2.20,
        }
        res = self.client.post(BOOK_URL, data=data)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
