from datetime import date, timedelta
from django.db.models import Q
from projectapp.models import ProjectModel, CompanyModel


from django.db.models import Q
from projectapp.models import ProjectModel

def get_company_feedback_activity(company_name=None, location_name=None, start_range=None, end_range=None):
    results = []

    qs = ProjectModel.has_feedback.select_related('company_name', 'location', 'project_format', 'days_format')\
        .prefetch_related('feedbacks__attachments').distinct()

    # فیلتر بر اساس شرکت
    if company_name:
        qs = qs.filter(company_name__name__iexact=company_name)

    # فیلتر بر اساس لوکیشن
    if location_name:
        qs = qs.filter(location__name__iexact=location_name)

    # فیلتر بر اساس بازه زمانی
    if start_range and end_range:
        qs = qs.filter(start_date__lte=end_range).filter(Q(end_date__gte=start_range) | Q(end_date__isnull=True))

    # گروه‌بندی بر اساس شرکت
    companies = {}
    for proj in qs:
        company = proj.company_name.name
        loc_name = proj.location_name.name

        if company not in companies:
            companies[company] = {
                "company_name": company,
                "detail": []
            }

        feedbacks = []
        for fb in proj.feedbacks.all().distinct():
            # فیلتر feedback بر اساس تاریخ اگر start_range و end_range داده شده
            if start_range and end_range and not (start_range <= fb.date <= end_range):
                continue

            responses = []
            try:
                res = fb.responses
                if res:
                    responses.append({
                        "through": res.through,
                        "date": res.date,
                        "message": res.message,
                        "iso_form": res.iso_form,
                    })
            except Exception:
                pass

            attachments = []
            for attach in fb.attachments.all().distinct():
                attachments.append({
                    "file": attach.file
                })

            feedbacks.append({
                "name": fb.name,
                "phone_number": fb.phone_number,
                "through": fb.through,
                "date": fb.date,
                "message": fb.message,
                "attachments": attachments,
                "response": responses
            })

        companies[company]["detail"].append({
            "project_format": proj.project_format.name,
            "location_name": loc_name,
            "pk": proj.pk,
            "geometry": proj.location_name.geometry,  
            "start_date": proj.start_date,
            "end_date": proj.end_date,
            "days_format": proj.days_format.format_name,
            "is_active_now": proj.is_active_now,
            "feedbacks": feedbacks
        })

    results = list(companies.values())
    return results