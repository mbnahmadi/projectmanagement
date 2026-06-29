from datetime import datetime
from django.utils.text import slugify
import os

def feedback_file_path(instance, filename):
    today = datetime.now()
    company_name = slugify(instance.feedback.project.company_name)
    return os.path.join(
        "feedbacks",
        f"{company_name}",
        str(today.year),
        str(today.month),
        str(today.day),
        filename
    )


def feedback_ISO_file_path(instance, filename):
    today = datetime.now()
    company_name = slugify(instance.feedback.project.company_name)
    return os.path.join(
        "feedbacks/ISO/",
        f"{company_name}",
        str(today.year),
        str(today.month),
        str(today.day),
        filename
    )

def location_file_path(instance, filename):
    today = datetime.now()
    company_name = slugify(instance.company_name)
    location_name = slugify(instance.location_name)
    # مسیر مثلا: profile_images/2025/08/10/user_23/filename.jpg
    return os.path.join(
        "projects_attachment/",
        f"{company_name}",
        f"{location_name}",
        str(today.year),
        str(today.month),
        str(today.day),
        filename
    )