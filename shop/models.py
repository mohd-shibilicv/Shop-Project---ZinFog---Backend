from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    product_image = models.ImageField(upload_to="product_images/", null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    average_rating = models.FloatField(default=0)

    def __str__(self):
        return self.name
    
    def __init__(self, *args, **kwargs):
        super(Product, self).__init__(*args, **kwargs)
        if not self.product_image:
            self.product_image = "product_images/product_image.png"


class Order(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
    ]

    customer = models.ForeignKey("customer.Customer", on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, through="OrderItem")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    address = models.ForeignKey("customer.Address", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} - {self.customer.user.first_name} {self.customer.user.last_name}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"Order {self.order.id}"
