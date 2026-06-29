from django_filters import rest_framework as filters
from django.db.models import Q
from rest_framework.serializers import SlugRelatedField
from .models import ProjectModel

class ProjectFilter(filters.FilterSet):
    start_date = filters.DateFilter(method='filter_by_date_range')
    end_date = filters.DateFilter(method='filter_by_date_range')
    company_name = filters.CharFilter(field_name='company_name__name', lookup_expr='iexact')
    location = filters.CharFilter(field_name='location_name', lookup_expr='iexact')

    def filter_by_date_range(self, queryset, name, value):
        # دریافت start_date و end_date از درخواست کاربر
        start_date = self.data.get('start_date')
        end_date = self.data.get('end_date')

        if start_date and end_date:
            return queryset.filter(
                # شرط 1: پروژه‌هایی که start_date و end_date در بازه مشخص هستند
                Q(start_date__gte=start_date, end_date__lte=end_date) |
                # شرط 2: پروژه‌هایی که end_date خالی است و start_date در بازه است
                Q(start_date__gte=start_date, start_date__lte=end_date, end_date__isnull=True)
            )
        # اگر فقط یکی از تاریخ‌ها ارائه شده باشد، می‌توانید منطق دیگری اعمال کنید
        elif start_date:
            return queryset.filter(start_date__gte=start_date)
        elif end_date:
            return queryset.filter(end_date__lte=end_date, end_date__isnull=False)

        return queryset

    class Meta:
        models = ProjectModel
        fields = '__all__'