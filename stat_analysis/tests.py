from django.test import TestCase
from stat_analysis.models.report import Report
from stat_analysis.models.statistics import JobReportResult, OrderReportResult, UserReportResult
from stat_analysis.stat_utils import calculate_job_stats, calculate_order_stats, calculate_user_stats
from execution.models import Job
from orders.models import Order, Product, ServiceProvider
from accounts.models import Customer, AccountManager, User
from datetime import datetime

class StatUtilsTestCase(TestCase):
    def setUp(self):
        # Setup minimal data for statistics tests
        user = User.objects.create(username='manager', role='account_manager')
        manager = AccountManager.objects.create(user=user)
        customer_user = User.objects.create(username='customer', role='customer')
        customer = Customer.objects.create(user=customer_user)
        provider = ServiceProvider.objects.create(name='Provider1')
        provider.managers.add(manager)
        product = Product.objects.create(name='Prod1', description='desc', service_provider=provider, price=100)
        # Create order with created_at in Q1 2025
        order = Order.objects.create(customer=customer, account_manager=manager)
        order.products.add(product)
        Order.objects.filter(id=order.id).update(created_at=datetime(2025, 1, 15))
        job = Job.objects.create(job_id='J1', job_name='Job1', state='completed', job_type='regular', starting_date=datetime(2025,1,1), end_date=datetime(2025,1,2), completion_time=1)
        job.orders.add(order)
        self.report = Report.objects.create(title='Test Report', created_by=user, quarter_from='Q1', year_from=2025, quarter_to='Q1', year_to=2025)

    def test_job_stats(self):
        stats = calculate_job_stats('Q1', 2025, 'Q1', 2025, self.report)
        self.assertEqual(stats.total_jobs, 1)
        self.assertIn('regular', stats.average_completion_time_per_type)
        self.assertIn('completed', stats.jobs_per_status)

    def test_order_stats(self):
        stats = calculate_order_stats('Q1', 2025, 'Q1', 2025, self.report)
        self.assertEqual(stats.total_orders, 1)
        self.assertEqual(float(stats.total_revenue), 100)
        self.assertEqual(float(stats.average_order_value), 100)

    def test_user_stats(self):
        stats = calculate_user_stats('Q1', 2025, 'Q1', 2025, self.report)
        self.assertEqual(stats.total_customers_handled, 1)
        self.assertEqual(stats.total_orders_created, 1)
