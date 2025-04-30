from django.db import models
from accounts.models import Customer, AccountManager, User

class ServiceProvider(models.Model):
    name = models.CharField(max_length=100)
    managers = models.ManyToManyField(AccountManager, related_name='service_providers')

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    service_provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Add price for statistics

    def __str__(self):
        return self.name

class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    account_manager = models.ForeignKey(AccountManager, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} by {self.customer}"

    def clean(self):
        # Enforce that all products are from service providers managed by the account manager
        allowed_providers = set(self.account_manager.service_providers.values_list('id', flat=True))
        for product in self.products.all():
            if product.service_provider_id not in allowed_providers:
                from django.core.exceptions import ValidationError
                raise ValidationError(f"Product '{product.name}' is not from a service provider managed by this account manager.")
