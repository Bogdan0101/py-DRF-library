from django.urls import path, include
from rest_framework import routers
from library.views import (
    BookViewSet,
    BorrowingViewSet,
    PaymentViewSet,
)

router = routers.DefaultRouter()
router.register("books", BookViewSet, basename="books")
router.register("borrowings", BorrowingViewSet, basename="borrowings")
router.register("payments", PaymentViewSet, basename="payments")
urlpatterns = [
    path("", include(router.urls)),
    path("payments/", include("library.payments.urls")),
]

app_name = "library"
