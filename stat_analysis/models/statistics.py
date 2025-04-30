from django.db import models
from .report import Report  # Import Report model

class JobReportResult(models.Model):
    """Model to store analysis results for the Jobs."""
    report = models.OneToOneField(Report, on_delete=models.CASCADE)
    total_jobs = models.IntegerField()
    average_completion_time_per_type = models.JSONField(default=dict)  # {job_type: avg_time}
    jobs_per_status = models.JSONField(default=dict)  # {status: count}

class OrderReportResult(models.Model):
    """Model to store analysis results for the customer Orders."""
    report = models.OneToOneField(Report, on_delete=models.CASCADE)

    total_orders = models.IntegerField()
    total_revenue = models.DecimalField(max_digits=10, decimal_places=2)
    average_order_value = models.DecimalField(max_digits=10, decimal_places=2)

class UserReportResult(models.Model):
    """Model to store analysis results for the Users (Account Managers, Customers)."""
    report = models.OneToOneField(Report, on_delete=models.CASCADE)

    total_customers_handled = models.IntegerField()
    total_orders_created = models.IntegerField()

