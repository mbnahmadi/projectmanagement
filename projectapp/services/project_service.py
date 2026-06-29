from datetime import date, timedelta
from django.db.models import Q
from projectapp.models import ProjectModel, CompanyModel

# def get_unique_active_days_by_company(start_range, end_range):
#     """
#     برگرداندن تعداد روزهای یکتای فعال بودن هر شرکت در بازه داده شده
#     خروجی: [
#         {"company_id": 1, "company_name": "Company A", "active_days": 11},
#         {"company_id": 2, "company_name": "Company B", "active_days": 6},
#     ]
#     """
#     projects = ProjectModel.objects.filter(
#         start_date__lte=end_range
#     ).filter(
#         Q(end_date__gte=start_range) | Q(end_date__isnull=True)
#     ).select_related("company_name")

#     company_days = {}

#     for project in projects:
#         comp_id = project.company_name_id
#         comp_name = project.company_name.name

#         # تقاطع بازه پروژه با بازه کاربر
#         proj_start = max(project.start_date, start_range)
#         proj_end = min(project.end_date or end_range, end_range)

#         if proj_start > proj_end:
#             continue

#         if comp_id not in company_days:
#             company_days[comp_id] = {"name": comp_name, "days": set()}

#         delta = (proj_end - proj_start).days
#         for i in range(delta + 1):
#             company_days[comp_id]["days"].add(proj_start + timedelta(days=i))

#     # خروجی مرتب‌شده
#     result = []
#     for cid, data in company_days.items():
#         result.append({
#             "company_id": cid,
#             "company_name": data["name"],
#             "active_days": len(data["days"])
#         })

#     return result




# def get_company_points_activity(company_name, start_range, end_range):
#     results = []

#     company = CompanyModel.objects.filter(name__iexact=company_name).first()
#     print('companies:',company)
#     print('start_range:',start_range)
#     print('end_range:',end_range)
#     # for company in companies:
#     company_projects = ProjectModel.objects.filter(
#         company_name=company,
#         start_date__lte=end_range,
#     ).filter(
#         Q(end_date__gte=start_range) | Q(end_date__isnull=True)
#     )
#     print('company_projects:',company_projects)

#     points_data = []
#     total_days = 0
#     total_location = 0

#     for proj in company_projects:
#         active_start = max(proj.start_date, start_range)
#         active_end = min(proj.end_date if proj.end_date else end_range, end_range)
#         active_days = (active_end - active_start).days + 1

#         points_data.append({
#             "location_name": proj.location,
#             "active_days": active_days
#         })

#         total_days += active_days
#         total_location +=1

#     results.append({
#         # "company_id": company.id,
#         "company_name": proj.company_name,
#         "points": points_data,
#         "total_days": total_days,
#         "total_location": total_location
#     })

#     return results



def get_company_points_activity(company_name=None, location_name=None, start_range=None, end_range=None):
    results = []

    qs = ProjectModel.objects.select_related('company_name', 'location_name', 'project_format', 'days_format').all()

    if company_name:
        qs = qs.filter(company_name__name__iexact=company_name)

    if location_name:
        qs = qs.filter(location_name__name__iexact=location_name)

    if start_range and end_range:
        qs = qs.filter(start_date__lte=end_range).filter(Q(end_date__gte=start_range) | Q(end_date__isnull=True))

    companies = {}
    for proj in qs:
        company = proj.company_name.name
        loc_name = proj.location_name.name

        if company not in companies:
            companies[company] = {
                "company_name": company,
                "detail": [],
                "total_days": 0,
                "total_location_set": set()  # برای جلوگیری از تکراری شمردن
            }

        if start_range and end_range:
            active_start = max(proj.start_date, start_range)
            active_end = min(proj.end_date if proj.end_date else end_range, end_range)
            active_days = (active_end - active_start).days + 1
        else:
            today = date.today()
            active_start = proj.start_date
            active_end = min(proj.end_date if proj.end_date else today, today)
            active_days = (active_end - active_start).days + 1 if active_end >= active_start else 0

        companies[company]["detail"].append({
            "location_name": loc_name,
            "project_format": proj.project_format.name,
            "pk": proj.pk,
            "geometry": proj.location_name.geometry,  
            "start_date": proj.start_date,
            "end_date": proj.end_date,
            "days_format": proj.days_format.format_name,
            "is_active_now": proj.is_active_now,
            "active_days": active_days
        })

        companies[company]["total_days"] += active_days
        companies[company]["total_location_set"].add(loc_name)  # جلوگیری از تکراری شمردن

    # تبدیل set به تعداد کل
    for comp in companies.values():
        comp["total_location"] = len(comp.pop("total_location_set"))

    results = list(companies.values())
    return results