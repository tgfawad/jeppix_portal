from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from django.core.files.uploadedfile import SimpleUploadedFile

from accounts.models import User, Customer, AccountManager
from orders.models import Order, Product, ServiceProvider
from execution.models import Job
from .models.report import Report
from .models.statistics import JobReportResult, OrderReportResult, UserReportResult
from .stat_utils import calculate_job_stats, calculate_order_stats, calculate_user_stats

class StatisticsBaseTestCase(TestCase):
    def setUp(self):
        # Create users
        self.manager_user = User.objects.create_user(
            username='manager1',
            password='pass123',
            role='account_manager'
        )
        self.account_manager = AccountManager.objects.create(user=self.manager_user)
        
        self.customer_user = User.objects.create_user(
            username='customer1',
            password='pass123',
            role='customer'
        )
        self.customer = Customer.objects.create(user=self.customer_user)
        
        # Create service provider and product
        self.provider = ServiceProvider.objects.create(name='Test Provider')
        self.provider.managers.add(self.account_manager)
        self.product = Product.objects.create(
            name='Test Product',
            description='Test Description',
            service_provider=self.provider,
            price=Decimal('99.99')
        )
        
        # Create order in Q1 2025
        self.order = Order.objects.create(
            customer=self.customer,
            account_manager=self.account_manager
        )
        self.order.products.add(self.product)
        Order.objects.filter(id=self.order.id).update(
            created_at=timezone.datetime(2025, 1, 15, tzinfo=timezone.utc)
        )
        
        # Create job
        self.job = Job.objects.create(
            job_id='TEST001',
            job_name='Test Job',
            state='completed',
            job_type='regular',
            starting_date=timezone.datetime(2025, 1, 1, tzinfo=timezone.utc),
            end_date=timezone.datetime(2025, 1, 2, tzinfo=timezone.utc),
            completion_time=1.0
        )
        self.job.orders.add(self.order)
        
        # Create report
        self.report = Report.objects.create(
            title='Q1 2025 Report',
            created_by=self.manager_user,
            quarter_from='Q1',
            year_from=2025,
            quarter_to='Q1',
            year_to=2025
        )

class ReportModelTests(StatisticsBaseTestCase):
    def test_create_report(self):
        """Test creating a report"""
        self.assertEqual(str(self.report), 'Q1 2025 Report')
        self.assertEqual(self.report.quarter_from, 'Q1')
        self.assertEqual(self.report.year_from, 2025)

    def test_pdf_upload(self):
        """Test PDF file upload functionality"""
        # Create a dummy PDF file
        pdf_content = b'%PDF-1.4 Test PDF content'
        pdf_file = SimpleUploadedFile('test.pdf', pdf_content, content_type='application/pdf')
        
        self.report.pdf_file = pdf_file
        self.report.save()
        
        self.assertTrue(self.report.pdf_file.name.endswith('.pdf'))

    def test_report_date_validation(self):
        """Test report date validation"""
        with self.assertRaises(ValidationError):
            Report.objects.create(
                title='Invalid Report',
                created_by=self.manager_user,
                quarter_from='Q5',  # Invalid quarter
                year_from=2025,
                quarter_to='Q1',
                year_to=2025
            )

class JobStatisticsTests(StatisticsBaseTestCase):
    def test_job_statistics_calculation(self):
        """Test job statistics calculation"""
        stats = calculate_job_stats('Q1', 2025, 'Q1', 2025, self.report)
        
        self.assertEqual(stats.total_jobs, 1)
        self.assertEqual(stats.jobs_per_status['completed'], 1)
        self.assertEqual(
            stats.average_completion_time_per_type['regular'],
            self.job.completion_time
        )

    def test_empty_period_statistics(self):
        """Test statistics for period with no jobs"""
        stats = calculate_job_stats('Q2', 2025, 'Q2', 2025, self.report)
        
        self.assertEqual(stats.total_jobs, 0)
        self.assertEqual(stats.jobs_per_status, {})
        self.assertEqual(stats.average_completion_time_per_type, {})

class OrderStatisticsTests(StatisticsBaseTestCase):
    def test_order_statistics_calculation(self):
        """Test order statistics calculation"""
        stats = calculate_order_stats('Q1', 2025, 'Q1', 2025, self.report)
        
        self.assertEqual(stats.total_orders, 1)
        self.assertEqual(stats.total_revenue, self.product.price)
        self.assertEqual(stats.average_order_value, self.product.price)

    def test_multiple_orders_statistics(self):
        """Test statistics with multiple orders"""
        # Create another order
        order2 = Order.objects.create(
            customer=self.customer,
            account_manager=self.account_manager
        )
        order2.products.add(self.product)
        Order.objects.filter(id=order2.id).update(
            created_at=timezone.datetime(2025, 1, 20, tzinfo=timezone.utc)
        )
        
        stats = calculate_order_stats('Q1', 2025, 'Q1', 2025, self.report)
        
        self.assertEqual(stats.total_orders, 2)
        self.assertEqual(stats.total_revenue, self.product.price * 2)
        self.assertEqual(stats.average_order_value, self.product.price)

class UserStatisticsTests(StatisticsBaseTestCase):
    def test_user_statistics_calculation(self):
        """Test user statistics calculation"""
        stats = calculate_user_stats('Q1', 2025, 'Q1', 2025, self.report)
        
        self.assertEqual(stats.total_customers_handled, 1)
        self.assertEqual(stats.total_orders_created, 1)

    def test_multiple_customers_statistics(self):
        """Test statistics with multiple customers"""
        # Create another customer and order
        customer2_user = User.objects.create_user(
            username='customer2',
            password='pass123',
            role='customer'
        )
        customer2 = Customer.objects.create(user=customer2_user)
        
        order2 = Order.objects.create(
            customer=customer2,
            account_manager=self.account_manager
        )
        Order.objects.filter(id=order2.id).update(
            created_at=timezone.datetime(2025, 1, 20, tzinfo=timezone.utc)
        )
        
        stats = calculate_user_stats('Q1', 2025, 'Q1', 2025, self.report)
        
        self.assertEqual(stats.total_customers_handled, 2)
        self.assertEqual(stats.total_orders_created, 2)
