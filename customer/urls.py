from django.urls import path, include
from rest_framework.routers import DefaultRouter

from customer.views import (
    AddressDetailView,
    AddressListCreateView,
    ProductViewSet,
    CartViewSet,
    CartItemViewSet,
    CustomerOrderViewSet,
    RatingViewSet,
)


router = DefaultRouter()
router.register(r"products", ProductViewSet, basename="product")
router.register(r"cart", CartViewSet, basename="cart")
router.register(r"cart-items", CartItemViewSet, basename="cartitem")
router.register(r"customer-orders", CustomerOrderViewSet, basename="customerorder")
router.register(r"ratings", RatingViewSet, basename="rating")


urlpatterns = [
    path("", include(router.urls)),
    path("addresses/", AddressListCreateView.as_view(), name="address-list-create"),
    path("addresses/<int:pk>/", AddressDetailView.as_view(), name="address-detail"),
]
