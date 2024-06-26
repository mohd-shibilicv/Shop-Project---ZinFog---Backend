from rest_framework import serializers
from .models import Product, Order, OrderItem
from customer.models import Customer, Address


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "description",
            "product_image",
            "price",
            "average_rating",
        ]


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ["id", "order", "product", "quantity"]


class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, read_only=True)
    customer = serializers.PrimaryKeyRelatedField(queryset=Customer.objects.all())
    address = serializers.PrimaryKeyRelatedField(queryset=Address.objects.all())
    products = serializers.ListField(child=serializers.IntegerField(), write_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "customer",
            "products",
            "status",
            "address",
            "created_at",
            "order_items",
        ]

    def create(self, validated_data):
        products = validated_data.pop("products")
        order = Order.objects.create(**validated_data)
        for product_id in products:
            OrderItem.objects.create(order=order, product_id=product_id, quantity=1)
        return order

    def update(self, instance, validated_data):
        products = validated_data.pop("products", None)
        instance.customer = validated_data.get("customer", instance.customer)
        instance.status = validated_data.get("status", instance.status)
        instance.address = validated_data.get("address", instance.address)
        instance.save()

        if products is not None:
            instance.order_items.all().delete()  # Clear existing items
            for product_id in products:
                OrderItem.objects.create(
                    order=instance, product_id=product_id, quantity=1
                )
        return instance
