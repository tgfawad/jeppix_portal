from django.contrib import admin
from .models import Report
from .models.statistics import JobReportResult, OrderReportResult, UserReportResult

admin.site.register(Report)
admin.site.register(JobReportResult)
admin.site.register(OrderReportResult)
admin.site.register(UserReportResult)
