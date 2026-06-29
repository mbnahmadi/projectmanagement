from collections import defaultdict
from datetime import date, datetime
import calendar
from django.db.models import Min, Max
from projectapp.models import ProjectModel

def calculate_days_per_month_all_years(filter_year=None):
    """
    Returns list of { year: YYYY, data: [ {month: 'Jan', days: n}, ... ] }
    اگر filter_year داده شود فقط همان سال محاسبه می‌شود.
    """
    qs = ProjectModel.objects.values('start_date', 'end_date')

    # تعیین بازه کلی سال‌ها
    agg = ProjectModel.objects.aggregate(min_start=Min('start_date'), max_end=Max('end_date'))
    min_start = agg.get('min_start')
    max_end = agg.get('max_end')

    if not min_start and not max_end:
        return []

    today = date.today()
    # today = datetime(2025,10,1).date()
    # print(type(today))
    # اگر کاربر سال خاصی خواسته:
    if filter_year:
        min_year = max_year = int(filter_year)
    else:
        min_year = (min_start or max_end).year
        max_year = (max_end or min_start or today).year

    totals = {year: defaultdict(int) for year in range(min_year, max_year + 1)}

    # پر کردن داده‌ها
    for item in qs:
        start = item.get('start_date')
        end = item.get('end_date') or today
        if not start or start > end:
            continue

        # اگر کاربر سال خاص داده و پروژه اصلاً در آن سال نیست، ردش کنیم
        if filter_year and (end.year < int(filter_year) or start.year > int(filter_year)):
            continue

        cur_year = start.year
        cur_month = start.month
        while (cur_year < end.year) or (cur_year == end.year and cur_month <= end.month):
            if filter_year and cur_year != int(filter_year):
                # اگر سال فیلتر شده است فقط همان سال را پردازش کن
                pass
            else:
                days_in_month = calendar.monthrange(cur_year, cur_month)[1]
                month_start = date(cur_year, cur_month, 1)
                month_end = date(cur_year, cur_month, days_in_month)

                overlap_start = max(start, month_start)
                overlap_end = min(end, month_end)
                if overlap_start <= overlap_end:
                    num_days = (overlap_end - overlap_start).days + 1
                    totals[cur_year][cur_month] += num_days

            # جلو بردن ماه
            if cur_month == 12:
                cur_month = 1
                cur_year += 1
            else:
                cur_month += 1

    # تبدیل به خروجی نهایی با حذف صفرهای ابتدا و انتها
    result = []
    years_to_return = [int(filter_year)] if filter_year else range(min_year, max_year + 1)

    for year in years_to_return:
        month_days = [int(totals.get(year, {}).get(m, 0)) for m in range(1, 13)]

        # پیدا کردن اولین و آخرین ماه غیر صفر
        first_nonzero = next((i for i, d in enumerate(month_days) if d > 0), None)
        last_nonzero = len(month_days) - 1 - next((i for i, d in enumerate(reversed(month_days)) if d > 0), None)

        # اگر کل سال صفر بود، پرش کن
        if first_nonzero is None:
            continue

        months_list = []
        for m in range(first_nonzero + 1, last_nonzero + 2):  # +1 چون اندیس‌ها 0-based هستند
            months_list.append({
                "month": calendar.month_abbr[m],
                "days": month_days[m - 1]
            })

        result.append({
            "year": year,
            "data": months_list
        })

    return result




def get_company_location_ranges(company_name_filter=None):

    qs = ProjectModel.objects.all().select_related('company_name', 'location')
    if company_name_filter:
        qs = qs.filter(company_name__name__iexact=company_name_filter)

    companies = defaultdict(lambda: defaultdict(list))

    for proj in qs:
        company = proj.company_name.name
        location = proj.location.name
        companies[company][location].append({
            "start_date": proj.start_date,
            "end_date": proj.end_date
        })

    result = []
    for company, locs in companies.items():
        locations_list = []
        for location, projects in locs.items():
            locations_list.append({
                "location": location,
                "range": projects
            })
        result.append({
            "company": company,
            "locations": locations_list
        })

    return result