from django.test import TestCase
from django.core.exceptions import ValidationError
from decimal import Decimal
from accounts.models import User, Customer, AccountManager
from .models import ServiceProvider, Product, Order

class ServiceProviderModelTests(TestCase):
    def setUp(self):
        # Create account manager
        self.manager_user = User.objects.create_user(
            username='manager1',
            password='pass123',
            role='account_manager'
        )
        self.account_manager = AccountManager.objects.create(user=self.manager_user)
        
        # Create another account manager for testing
        self.manager_user2 = User.objects.create_user(
            username='manager2',
            password='pass123',
            role='account_manager'
        )
        self.account_manager2 = AccountManager.objects.create(user=self.manager_user2)

    def test_create_service_provider(self):
        """Test creating a service provider"""
        provider = ServiceProvider.objects.create(name='Test Provider')
        provider.managers.add(self.account_manager)
        
        self.assertEqual(str(provider), 'Test Provider')
        self.assertEqual(provider.managers.count(), 1)
        self.assertIn(self.account_manager, provider.managers.all())

    def test_multiple_managers(self):
        """Test service provider can have multiple managers"""
        provider = ServiceProvider.objects.create(name='Test Provider')
        provider.managers.add(self.account_manager, self.account_manager2)
        
        self.assertEqual(provider.managers.count(), 2)
        self.assertIn(self.account_manager2, provider.managers.all())

class ProductModelTests(TestCase):
    def setUp(self):
        self.service_provider = ServiceProvider.objects.create(name='Test Provider')

    def test_create_product(self):
        """Test creating a product"""
        product = Product.objects.create(
            name='Test Product',
            description='Test Description',
            service_provider=self.service_provider,
            price=Decimal('99.99')
        )
        
        self.assertEqual(str(product), 'Test Product')
        self.assertEqual(product.service_provider, self.service_provider)
        self.assertEqual(product.price, Decimal('99.99'))

    def test_product_price_validation(self):
        """Test product price validation"""
        # Test negative price
        with self.assertRaises(ValidationError):
            product = Product.objects.create(
                name='Test Product',
                description='Test Description',
                service_provider=self.service_provider,
                price=Decimal('-10.00')
            )
            product.full_clean()

class OrderModelTests(TestCase):
    def setUp(self):
        # Create customer
        self.customer_user = User.objects.create_user(
            username='customer1',
            password='pass123',
            role='customer'
        )
        self.customer = Customer.objects.create(user=self.customer_user)
        
        # Create account manager
        self.manager_user = User.objects.create_user(
            username='manager1',
            password='pass123',
            role='account_manager'
        )
        self.account_manager = AccountManager.objects.create(user=self.manager_user)
        
        # Create service provider and product
        self.service_provider = ServiceProvider.objects.create(name='Test Provider')
        self.service_provider.managers.add(self.account_manager)
        
        self.product = Product.objects.create(
            name='Test Product',
            description='Test Description',
            service_provider=self.service_provider,
            price=Decimal('99.99')
        )

    def test_create_order(self):
        """Test creating an order"""
        order = Order.objects.create(
            customer=self.customer,
            account_manager=self.account_manager
        )
        order.products.add(self.product)
        
        self.assertEqual(str(order), f"Order #{order.id} by {self.customer}")
        self.assertEqual(order.products.count(), 1)
        self.assertIn(self.product, order.products.all())

    def test_order_validation(self):
        """Test order validation for product service provider"""
        # Create another manager and provider
        manager2_user = User.objects.create_user(
            username='manager2',
            password='pass123',
            role='account_manager'
        )
        manager2 = AccountManager.objects.create(user=manager2_user)
        provider2 = ServiceProvider.objects.create(name='Provider 2')
        provider2.managers.add(manager2)
        product2 = Product.objects.create(
            name='Product 2',
            description='Description 2',
            service_provider=provider2,
            price=Decimal('149.99')
        )
        
        # Create order with product from unauthorized service provider
        order = Order.objects.create(
            customer=self.customer,
            account_manager=self.account_manager
        )
        order.products.add(product2)
        
        with self.assertRaises(ValidationError):
            order.clean()

    def test_order_visibility(self):
        """Test order visibility for different account managers"""
        # Create order with first manager
        order1 = Order.objects.create(
            customer=self.customer,
            account_manager=self.account_manager
        )
        
        # Create another manager
        manager2_user = User.objects.create_user(
            username='manager2',
            password='pass123',
            role='account_manager'
        )
        manager2 = AccountManager.objects.create(user=manager2_user)
        
        # Check that manager2 cannot see order1
        manager1_orders = Order.objects.filter(account_manager=self.account_manager)
        manager2_orders = Order.objects.filter(account_manager=manager2)
        
        self.assertIn(order1, manager1_orders)
        self.assertNotIn(order1, manager2_orders)

    def test_multiple_orders_same_customer(self):
        """Test multiple orders for the same customer"""
        order1 = Order.objects.create(
            customer=self.customer,
            account_manager=self.account_manager
        )
        order2 = Order.objects.create(
            customer=self.customer,
            account_manager=self.account_manager
        )
        
        customer_orders = Order.objects.filter(customer=self.customer)
        self.assertEqual(customer_orders.count(), 2)
        self.assertIn(order1, customer_orders)
        self.assertIn(order2, customer_orders)
