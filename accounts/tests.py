from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from .models import Customer, AccountManager, User

class UserModelTests(TestCase):
    def setUp(self):
        self.user_data = {
            'username': 'testuser',
            'password': 'testpass123',
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User'
        }

    def test_create_user(self):
        """Test creating a regular user"""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.username, self.user_data['username'])
        self.assertTrue(user.check_password(self.user_data['password']))
        self.assertEqual(user.role, 'customer')  # Default role

    def test_create_superuser(self):
        """Test creating a superuser"""
        admin = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123'
        )
        self.assertTrue(admin.is_superuser)
        self.assertTrue(admin.is_staff)

    def test_user_role_choices(self):
        """Test user role validation"""
        user = User.objects.create_user(**self.user_data)
        
        # Test valid role
        user.role = 'account_manager'
        user.full_clean()  # Should not raise ValidationError
        
        # Test invalid role
        with self.assertRaises(ValidationError):
            user.role = 'invalid_role'
            user.full_clean()

class CustomerModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='customer1',
            password='pass123',
            role='customer'
        )

    def test_create_customer(self):
        """Test creating a customer profile"""
        customer = Customer.objects.create(user=self.user)
        self.assertEqual(str(customer), 'customer1')
        self.assertEqual(customer.user.role, 'customer')

    def test_customer_user_relationship(self):
        """Test one-to-one relationship between Customer and User"""
        customer1 = Customer.objects.create(user=self.user)
        
        # Try to create another customer with same user
        user2 = User.objects.create_user(
            username='customer2',
            password='pass123',
            role='customer'
        )
        Customer.objects.create(user=user2)
        
        self.assertEqual(Customer.objects.count(), 2)
        self.assertEqual(customer1.user, self.user)

class AccountManagerModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='manager1',
            password='pass123',
            role='account_manager'
        )

    def test_create_account_manager(self):
        """Test creating an account manager profile"""
        manager = AccountManager.objects.create(user=self.user)
        self.assertEqual(str(manager), 'manager1')
        self.assertEqual(manager.user.role, 'account_manager')

    def test_account_manager_user_relationship(self):
        """Test one-to-one relationship between AccountManager and User"""
        manager1 = AccountManager.objects.create(user=self.user)
        
        # Try to create another manager with same user
        with self.assertRaises(Exception):
            AccountManager.objects.create(user=self.user)
        
        self.assertEqual(AccountManager.objects.count(), 1)

class UserAuthenticationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )

    def test_user_authentication(self):
        """Test user authentication functionality"""
        from django.contrib.auth import authenticate
        
        # Test with correct credentials
        authenticated_user = authenticate(
            username='testuser',
            password='testpass123'
        )
        self.assertIsNotNone(authenticated_user)
        self.assertEqual(authenticated_user, self.user)
        
        # Test with incorrect password
        wrong_user = authenticate(
            username='testuser',
            password='wrongpass'
        )
        self.assertIsNone(wrong_user)
        
        # Test with non-existent username
        nonexistent_user = authenticate(
            username='nonexistent',
            password='testpass123'
        )
        self.assertIsNone(nonexistent_user)
