from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from accounts.models import User, Customer, AccountManager
from orders.models import Order, Product, ServiceProvider
from .models import Job

class JobModelTests(TestCase):
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
        
        # Create order
        self.order = Order.objects.create(
            customer=self.customer,
            account_manager=self.account_manager
        )

        # Set up base job data
        self.now = timezone.now()
        self.job_data = {
            'job_id': 'TEST001',
            'job_name': 'Test Job',
            'state': 'created',
            'job_type': 'regular',
            'starting_date': self.now,
            'end_date': self.now + timedelta(days=1),
            'completion_time': 1.0
        }

    def test_create_job(self):
        """Test creating a job"""
        job = Job.objects.create(**self.job_data)
        job.orders.add(self.order)
        
        self.assertEqual(str(job), 'Test Job')
        self.assertEqual(job.state, 'created')
        self.assertEqual(job.job_type, 'regular')
        self.assertEqual(job.orders.count(), 1)
        self.assertIn(self.order, job.orders.all())

    def test_job_state_validation(self):
        """Test job state validation"""
        job = Job.objects.create(**self.job_data)
        
        # Test valid state transition
        job.state = 'active'
        job.full_clean()  # Should not raise ValidationError
        
        # Test invalid state
        with self.assertRaises(ValidationError):
            job.state = 'invalid_state'
            job.full_clean()

    def test_job_type_validation(self):
        """Test job type validation"""
        job = Job.objects.create(**self.job_data)
        
        # Test valid job type
        job.job_type = 'wafer_run'
        job.full_clean()  # Should not raise ValidationError
        
        # Test invalid job type
        with self.assertRaises(ValidationError):
            job.job_type = 'invalid_type'
            job.full_clean()

    def test_job_dates_validation(self):
        """Test job dates validation"""
        # Test end_date before starting_date
        invalid_job_data = self.job_data.copy()
        invalid_job_data['end_date'] = self.now - timedelta(days=1)
        
        job = Job.objects.create(**invalid_job_data)
        with self.assertRaises(ValidationError):
            job.full_clean()

    def test_multiple_orders_per_job(self):
        """Test associating multiple orders with a job"""
        job = Job.objects.create(**self.job_data)
        
        # Create another order
        order2 = Order.objects.create(
            customer=self.customer,
            account_manager=self.account_manager
        )
        
        # Add both orders to the job
        job.orders.add(self.order, order2)
        
        self.assertEqual(job.orders.count(), 2)
        self.assertIn(self.order, job.orders.all())
        self.assertIn(order2, job.orders.all())

    def test_completion_time_calculation(self):
        """Test job completion time calculation"""
        job = Job.objects.create(**self.job_data)
        
        # Verify completion time matches the difference between end_date and starting_date
        expected_completion_time = (job.end_date - job.starting_date).total_seconds() / (24 * 3600)  # Convert to days
        self.assertAlmostEqual(job.completion_time, expected_completion_time, places=2)

    def test_job_lifecycle(self):
        """Test job state transitions through its lifecycle"""
        job = Job.objects.create(**self.job_data)
        
        # Test state transitions
        self.assertEqual(job.state, 'created')
        
        job.state = 'active'
        job.save()
        self.assertEqual(job.state, 'active')
        
        job.state = 'completed'
        job.save()
        self.assertEqual(job.state, 'completed')
