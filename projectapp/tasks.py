import os
import logging
import datetime
from celery import shared_task
from .models import ProjectModel
from django.conf import settings
from django.core.cache import cache

BASE_ADDRESS_OF_PDFS_ON_SERVER = settings.BASE_ADDRESS_OF_PDFS_ON_SERVER

# @shared_task
# def update_active_projects_pdfs():
#     qs = ProjectModel.active_locations.only('id', 'project_address', 'latest_pdf_path').iterator()
#     companies = set()
#     for p in qs:
#         if p.project_address:
#             companies.add(p.project_address.split('/', 1)[0])
#     for company in companies:
#         cache.delete(f'latest_gfs_{company}')
#     active_projects = ProjectModel.active_locations.only('id', 'project_address', 'latest_pdf_path').iterator()
#     for project in active_projects:
#         new_path = project.generate_latest_pdf_address()
#         if new_path and new_path != project.latest_pdf_path:
#             ProjectModel.objects.filter(id=project.id).update(latest_pdf_path=new_path)



# @shared_task
# def update_active_projects_pdfs():
#     projects_qs = ProjectModel.active_locations.only('id', 'project_address', 'latest_pdf_path').iterator() 
#     companies_map = {} # {'company_name': [project_id, ...]}
#     projects_data = {} # {project_id: {'project_address': ..., 'old_path': ...}}

#     for p in projects_qs:
#         if p.project_address:
#             company = p.project_address.split('/', 1)[0]
#             if company not in companies_map:
#                 companies_map[company] = []
#             companies_map[company].append(p.id)
#             projects_data[p.id] = {'project_address': p.project_address, 'old_path': p.latest_pdf_path}

#     for company in companies_map.keys():
#         base_path = os.path.join(BASE_ADDRESS_OF_PDFS_ON_SERVER, company)
#         if not os.path.exists(base_path):
#             logger.warning(f"Base path not found for company: {company} at {base_path}")
#             continue

#         try:
#             gfs_folders = [f for f in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, f))]
#             if not gfs_folders:
#                 logger.warning(f"No GFS folders found for company: {company}")
#                 continue
            
#             latest_gfs = max(gfs_folders, key=lambda x: datetime.datetime.strptime(x[4:], '%Y%m%d%H') if x.startswith('gfs.') else datetime.min)
            
#             cache_key = f'latest_gfs_{company}'
#             # زمان کش را کمتر از ۱۲ ساعت (مثلاً ۱۱ ساعت) تنظیم کنید تا اگر Celery شکست خورد، کش قدیمی منقضی شود.
#             cache.set(cache_key, latest_gfs, 60 * 60 * 11) 

#         except Exception as e:
#             logger.error(f"Error processing GFS folders for company {company}: {e}")
#             continue
    
#     updates_to_perform = [] # لیست کردن تغییرات

#     for project_id, data in projects_data.items():
#         project = ProjectModel.objects.get(id=project_id)
#         new_path = project.generate_latest_pdf_address()
        
#         if new_path and new_path != data['old_path']:
#             # به‌جای دیکشنری، یک تاپل شامل (ID, مسیر جدید) برای به‌روزرسانی نهایی ذخیره کنید
#             updates_to_perform.append((project_id, new_path)) 
            
#             # 👇 لاگ بگیرید که این پروژه قرار است آپدیت شود
#             logger.info(f"PROJECT_UPDATE: Project ID {project.location_name} | Old PDF: '{data['old_path']}' | New PDF: '{new_path}'")
            
#         elif not new_path:
#             # 👇 لاگ بگیرید که چرا آپدیت نشد (مسیر فایل سرور مشکل دارد)
#             logger.warning(f"PROJECT_SKIP: Project ID {project.location_name} skipped. Reason: Could not generate new PDF path.")
        
#         # else: نیازی به آپدیت نیست (مسیر قدیمی با جدید برابر است)
#         # اگر می‌خواهید همه چیز لاگ شود:
#         # else: logger.debug(f"PROJECT_NO_CHANGE: Project ID {project_id} is up-to-date: '{new_path}'")

#     # 4. اجرای Bulk Update
#     if updates_to_perform:
#         # چون از filter().update() استفاده می‌کنید، باید در یک حلقه اجرا شود
#         for project_id, new_path in updates_to_perform:
#             ProjectModel.objects.filter(id=project_id).update(latest_pdf_path=new_path)
            
#         logger.info(f"TASK_SUMMARY: Successfully updated {len(updates_to_perform)} projects in the database.")
#     else:
#         logger.info("TASK_SUMMARY: No active projects required a PDF path update.")
    # 3. فاز Update: محاسبه مسیر جدید و به‌روزرسانی دیتابیس
    # updates_to_perform = {} # {project_id: new_path}

    # for project_id, data in projects_data.items():
    #     # متد generate_latest_pdf_address حالا به طور بهینه از کش (Cache) استفاده می‌کند.
    #     project = ProjectModel.objects.get(id=project_id) # دوباره شیء را می‌گیریم
    #     new_path = project.generate_latest_pdf_address()
        
    #     if new_path and new_path != data['old_path']:
    #         updates_to_perform[project_id] = new_path
    #         logger.info(f"Prepared to update ID {project_id}: Old='{data['old_path']}', New='{new_path}'")
    #     elif not new_path:
    #         logger.warning(f"Could not generate new PDF path for project ID {project_id}.")
    #     # else: مسیر همان است، نیازی به لاگ اطلاعات نیست.

    # # 4. اجرای Bulk Update: اجرای تنها یک کوئری (یا تعداد کمی) به جای کوئری به ازای هر پروژه
    # if updates_to_perform:
    #     # استفاده از متد‌های Bulk Update برای کاهش تعامل با دیتابیس در حجم بالا
    #     for project_id, new_path in updates_to_perform.items():
    #         ProjectModel.objects.filter(id=project_id).update(latest_pdf_path=new_path)
            
    #     logger.info(f"Successfully updated {len(updates_to_perform)} project paths in the database.")
    # else:
    #     logger.info("No active projects required a PDF path update.")



logger = logging.getLogger(__name__)

@shared_task()
def update_active_projects_pdfs():
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

        
        