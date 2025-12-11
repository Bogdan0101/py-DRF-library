from django.urls import path, include
from rest_framework import routers
from library.views import (
    BookViewSet,
    BorrowingViewSet,
)

router = routers.DefaultRouter()
router.register("book", BookViewSet, basename="books")
router.register("borrowing", BorrowingViewSet, basename="borrowings")
urlpatterns = [path("", include(router.urls))]

app_name = "library"
