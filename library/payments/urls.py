from django.urls import path
from library.payments.views import (stripe_success, stripe_cancel)

urlpatterns = [
    path("success/", stripe_success, name="stripe-success"),
    path("cancel/", stripe_cancel, name="stripe-cancel"),
]

app_name = "payments"
