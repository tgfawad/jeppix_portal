import datetime
from django.apps import apps
from django.db.models import Count, Avg, F, Sum

from execution.models import Job
from orders.models import Order
from accounts.models import AccountManager, Customer

# Correct way to get models dynamically
job_stats_model = apps.get_model("stat_analysis", "JobReportResult")
order_stats_model = apps.get_model("stat_analysis", "OrderReportResult")
user_stats_model = apps.get_model("stat_analysis", "UserReportResult")
report_model = apps.get_model("stat_analysis", "Report")


def get_quarter_dates(quarter, year):
    if quarter == 'Q1':
        start_date = datetime.date(year, 1, 1)
        end_date = datetime.date(year, 3, 31)
    elif quarter == 'Q2':
        start_date = datetime.date(year, 4, 1)
        end_date = datetime.date(year, 6, 30)
    elif quarter == 'Q3':
        start_date = datetime.date(year, 7, 1)
        end_date = datetime.date(year, 9, 30)
    elif quarter == 'Q4':
        start_date = datetime.date(year, 10, 1)
        end_date = datetime.date(year, 12, 31)
    else:
        raise ValueError("Invalid quarter. Please use 'Q1', 'Q2', 'Q3', or 'Q4'.")
    return start_date, end_date


def calculate_job_stats(quarter_from, year_from, quarter_to, year_to):
    """Calculate statistics for Job model for a given period."""

    start_date_from, end_date_from = get_quarter_dates(quarter_from, year_from)
    start_date_to, end_date_to = get_quarter_dates(quarter_to, year_to)

    start_date = min(start_date_from, start_date_to)
    end_date = max(end_date_from, end_date_to)

    jobs = Job.objects.filter(
        starting_date__gte=start_date,
        end_date__lte=end_date
    )

    total_jobs = jobs.count()

    report, created = report_model.objects.get_or_create(
        quarter_from=quarter_from,
        year_from=year_from,
        quarter_to=quarter_to,
        year_to=year_to,
        defaults={
            'title': 'Job Report',
            'created_at': datetime.datetime.now(),
            'created_by': 'system',  # You should replace 'system' with a User instance if needed
        }
    )

    job_stats, created = job_stats_model.objects.get_or_create(
        report=report,
        defaults={'total_jobs': total_jobs}
    )

    if not created:
        job_stats.total_jobs = total_jobs
        job_stats.save()

    # Additional requested statistics:
    avg_completion_time_by_type = jobs.values('job_type').annotate(avg_time=Avg('completion_time'))
    jobs_per_status = jobs.values('state').annotate(count=Count('id'))

    print("Average Completion Time by Job Type:")
    for entry in avg_completion_time_by_type:
        print(entry)

    print("Number of Jobs by Status:")
    for entry in jobs_per_status:
        print(entry)

    return job_stats


def calculate_order_stats(quarter_from, year_from, quarter_to, year_to):
    """Calculate statistics for Order model for a given period."""

    start_date_from, end_date_from = get_quarter_dates(quarter_from, year_from)
    start_date_to, end_date_to = get_quarter_dates(quarter_to, year_to)

    start_date = min(start_date_from, start_date_to)
    end_date = max(end_date_from, end_date_to)

    orders = Order.objects.filter(
        created_at__gte=start_date,
        created_at__lte=end_date
    )

    total_orders = orders.count()

    # Assuming each Product has a 'price' field (if not, you'll have to adjust)
    total_revenue = 0
    for order in orders:
        for product in order.products.all():
            total_revenue += getattr(product, 'price', 0)

    average_order_value = (total_revenue / total_orders) if total_orders else 0

    report, created = report_model.objects.get_or_create(
        quarter_from=quarter_from,
        year_from=year_from,
        quarter_to=quarter_to,
        year_to=year_to,
        defaults={
            'title': 'Order Report',
            'created_at': datetime.datetime.now(),
            'created_by': 'system',
        }
    )

    order_stats, created = order_stats_model.objects.get_or_create(
        report=report,
        defaults={
            'total_orders': total_orders,
            'total_revenue': total_revenue,
            'average_order_value': average_order_value
        }
    )

    if not created:
        order_stats.total_orders = total_orders
        order_stats.total_revenue = total_revenue
        order_stats.average_order_value = average_order_value
        order_stats.save()

    return order_stats


def calculate_user_stats(quarter_from, year_from, quarter_to, year_to):
    """Calculate statistics for Users."""

    start_date_from, end_date_from = get_quarter_dates(quarter_from, year_from)
    start_date_to, end_date_to = get_quarter_dates(quarter_to, year_to)

    start_date = min(start_date_from, start_date_to)
    end_date = max(end_date_from, end_date_to)

    total_customers = Customer.objects.count()
    total_orders = Order.objects.filter(
        created_at__gte=start_date,
        created_at__lte=end_date
    ).count()

    report, created = report_model.objects.get_or_create(
        quarter_from=quarter_from,
        year_from=year_from,
        quarter_to=quarter_to,
        year_to=year_to,
        defaults={
            'title': 'User Report',
            'created_at': datetime.datetime.now(),
            'created_by': 'system',
        } 
    )

    user_stats, created = user_stats_model.objects.get_or_create(
        report=report,
        defaults={
            'total_customers_handled': total_customers,
            'total_orders_created': total_orders
        }
    )

    if not created:
        user_stats.total_customers_handled = total_customers
        user_stats.total_orders_created = total_orders
        user_stats.save()

    return user_stats
