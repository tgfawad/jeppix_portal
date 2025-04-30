"""stat_analysis.models.report.py

"""
from django.db import models
from accounts.models import User  # Import User model

class Report(models.Model):
    # metadata
    title = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    # Report settings 
    quarter_from = models.CharField(max_length=2)  # Q1, Q2, Q3, Q4
    year_from = models.IntegerField()
    quarter_to = models.CharField(max_length=2)  # Q1, Q2, Q3, Q4
    year_to = models.IntegerField()

    pdf_file = models.FileField(upload_to='reports/', blank=True, null=True)  # Add PDF upload

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Import here to avoid AppRegistryNotReady error
        from stat_analysis.stat_utils import calculate_job_stats, calculate_order_stats, calculate_user_stats
        calculate_job_stats(self.quarter_from, self.year_from, self.quarter_to, self.year_to, self)
        calculate_order_stats(self.quarter_from, self.year_from, self.quarter_to, self.year_to, self)
        calculate_user_stats(self.quarter_from, self.year_from, self.quarter_to, self.year_to, self)

    def __str__(self):
        return self.title
