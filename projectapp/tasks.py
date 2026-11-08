import os
import logging
import datetime
from celery import shared_task
from .models import ProjectModel
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone
from .monitoring import record_task_success

BASE_ADDRESS_OF_PDFS_ON_SERVER = settings.BASE_ADDRESS_OF_PDFS_ON_SERVER

logger = logging.getLogger(__name__)


def get_monitor_type():
    now = timezone.localtime()
    if 5 <= now.hour < 6:
        return "morning"
    elif 17 <= now.hour < 18:
        return "evening"
    return None


def get_monitor_url():
    monitor_type = get_monitor_type()
    if monitor_type == "morning":
        return os.getenv("PM_MORNING_PUSH_URL")
    elif monitor_type == "evening":
        return os.getenv("PM_EVENING_PUSH_URL")
    return None


@shared_task()
def update_active_projects_pdfs():
    monitor_type = get_monitor_type()
    
    active_company = ProjectModel.active_locations.exclude(
        project_address__isnull=True
    ).select_related('company_name', 'location_name').iterator()
    
    for proj in active_company:
        new_path = proj.generate_latest_pdf_address()
        if new_path:
            proj.latest_pdf_path = new_path
            proj.save(update_fields=['latest_pdf_path'])
            logger.info(f"Generated PDF at {new_path} for project {proj.company_name.name} / {proj.location_name.name}")
        else:
            logger.warning(f"No PDF found for project {proj.company_name.name} / {proj.location_name.name}")

    if monitor_type:
        completed_at = timezone.localtime().isoformat()
        record_task_success(
            monitor_type,
            completed_at
        )