from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from customer.models import Customer, Product


User = get_user_model()


class RatingTestCase(APITestCase):
    def setUp(self):
        self.customer = Customer.objects.create(
            user=User.objects.create(email="test@example.com", password="Plo90plo90p!", is_active=True)
        )
        self.product = Product.objects.create(name="Test Product", price=100, description="Testing")

    def test_valid_rating(self):
        url = reverse("rating")
        data = {"customer": self.customer.id, "product": self.product.id, "rating": 5}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_invalid_rating(self):
        url = reverse("rating")
        data = {"customer": self.customer.id, "product": self.product.id, "rating": 6}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
