import os
import glob
import datetime
from decouple import config
from django.db import models
from django.contrib.gis.db import models as gis_models
from django.core.exceptions import ValidationError
from django.core.cache import cache
from core.files_path import location_file_path
from django.db.models import Q, F
from django.conf import settings
from django.utils.translation import gettext_lazy as _

BASE_ADDRESS_OF_PDFS_ON_SERVER = settings.BASE_ADDRESS_OF_PDFS_ON_SERVER


# ================== Reference Models ========================
class CompanyModel(models.Model):
    name = models.CharField(verbose_name=_('Company name'), max_length=255, unique=True)

    class Meta:
        verbose_name = _('Company')
        verbose_name_plural = _('companies')

    def __str__(self) -> str:
        return self.name


class DayFormatModel(models.Model):
    format_name = models.CharField(verbose_name=_('day format'), max_length=255, unique=True)

    class Meta:
        verbose_name = _('day format')
        verbose_name_plural = _('day formats')
        
    def __str__(self) -> str:
        return self.format_name


class ProjectFormatModel(models.Model):
    name = models.CharField(verbose_name=_('format name'), max_length=255, unique=True)

    class Meta:
        verbose_name = _('project format')
        verbose_name_plural = _('project formats')

    def __str__(self) -> str:
        return self.name


class LocationModel(models.Model):
    name = models.CharField(verbose_name=_('Location name'), max_length=255)
    geometry = gis_models.GeometryField(verbose_name=_('Geometry'), srid=4326, spatial_index=True, blank=False, null=False) 

    class Meta:
        verbose_name = _('location')
        verbose_name_plural = _('locations')
        
    def __str__(self) -> str:
        return f"{self.name}"

    def is_point(self):
        return self.geometry.geom_type == 'Point'

    def is_line(self):
        return self.geometry.geom_type == 'LineString'

    @property
    def display_point(self):
        if not self.geometry:
            return None
        if self.is_point():
            return self.geometry
        return self.geometry.centroid
    
    @property
    def lat(self):
        dp = self.display_point
        return None if dp is None else dp.y

    @property
    def lon(self):
        dp = self.display_point
        return None if dp is None else dp.x

    def clean(self):
        errors = {}
        # چیزی به جز لاین و پوینت نمیتونیم داشته باشیم
        if self.geometry and self.geometry.geom_type not in ('Point', 'LineString'):
            errors['geometry'] = _('Geometry must be Point or LineString.')

        if errors:
            raise ValidationError(errors)

# =========================================================

# =================== Manager =============================
class ActiveLocationsManager(models.Manager):
    def get_queryset(self):
        # فقط کوئری هایی که end_date, end_cycle انها خالی هست
        # return super().get_queryset().filter(is_active_now=True)
        return super().get_queryset().filter(end_date__isnull=True, end_cycle__isnull=True)


class HasFeedBackManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(feedbacks__isnull=False)


# =========== Project Model =============
class ProjectModel(models.Model):
    CYCLES_CHOICES = [
        ('1', _('cycle 1')),
        ('2', _('cycle 2'))
    ]
    project_format = models.ForeignKey('ProjectFormatModel', on_delete=models.PROTECT, related_name='project_format', default=1)
    company_name = models.ForeignKey('CompanyModel', on_delete=models.PROTECT, related_name='project')
    location_name = models.ForeignKey('LocationModel', on_delete=models.PROTECT, related_name='location')
    days_format = models.ForeignKey('DayFormatModel', on_delete=models.PROTECT, related_name='days_format')
    description = models.TextField(verbose_name=_('Description'), null=True, blank=True)
    attachment = models.FileField(upload_to=location_file_path, verbose_name=_('attachment'), null=True, blank=True)
    start_date = models.DateField(verbose_name=_('Start dateTime'))
    end_date = models.DateField(verbose_name=_('End dateTime'), null=True, blank=True)
    total_days = models.PositiveIntegerField(verbose_name=_('Total number of days'), default=0, editable=False)
    start_cycle = models.CharField(verbose_name=_('Start cycle'), choices=CYCLES_CHOICES, max_length=5, null=False, blank=False)
    end_cycle = models.CharField(verbose_name=_('End cycle'), choices=CYCLES_CHOICES, max_length=5,null=True, blank=True)
    total_cycle = models.PositiveIntegerField(verbose_name=_('Total cycle'), default=0, editable=False)
    is_active_now = models.BooleanField(verbose_name=_('is_active_now'), default=False, editable=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    project_address = models.CharField(max_length=256, null=True, blank=True, help_text='e.g-> AkamIndustry10Days_V01/SPD6')
    latest_pdf_path = models.CharField(verbose_name=_('Latest PDF path'), max_length=512,  null=True, blank=True)
    # editable=False

    # -------------------------------- Managers ----------------------------------------
    objects = models.Manager() # اصلی و شامل همه پروژه ها
    active_locations = ActiveLocationsManager() # فقط پروژه‌های بدون end_date و end_cycle
    has_feedback = HasFeedBackManager()

    # --------------------------------- Generate ----------------------------------------
    def generate_latest_pdf_address(self) -> str | None:
        if not self.project_address:
            return None

        company, location = self.project_address.split('/', 1)
        base_path = os.path.join(BASE_ADDRESS_OF_PDFS_ON_SERVER, company)  

        cache_key = f'latest_gfs_{company}'
        latest_gfs = cache.get(cache_key) 
        
        if not latest_gfs:
            if not os.path.exists(base_path):
                return None
            gfs_folders = [f for f in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, f))]
            if not gfs_folders:
                return None
            latest_gfs = max(gfs_folders, key=lambda x: datetime.datetime.strptime(x[4:], '%Y%m%d%H') if x.startswith('gfs.') else datetime.min)

        gfs_path = os.path.join(base_path, latest_gfs)
        
        pdf_files = glob.glob(os.path.join(gfs_path, f"{location}_*.pdf"))
        if not pdf_files:
            return None
        return pdf_files[0] 
    
    # ----------------------- Validations -----------------------------
    def clean(self):
        errors = {}

        if self.start_date and self.end_date and self.end_date < self.start_date:
            errors['end_date'] = _('End date cannot be before start date.')

        end_date_isnull = self.end_date is None
        end_cycle_isnull = self.end_cycle in (None, '')
        if (end_date_isnull != end_cycle_isnull):
            errors['end_date'] = _('end_date and end_cycle must be both null or both set.')
            errors['end_cycle'] = _('end_date and end_cycle must be both null or both set.')


        if (self.start_date and self.end_date and self.start_date == self.end_date
            and self.start_cycle and self.end_cycle):
            if int(self.end_cycle) < int(self.start_cycle):
                errors['end_cycle'] = _('End cycle cannot be before start cycle on the same day.')

        if errors:
            raise ValidationError(errors)

    # ----------------------- Save ------------------------------
    def save(self, *args, **kwargs):

        end_date_isnull = self.end_date is None
        end_cycle_isnull = self.end_cycle in (None, '')
        self.is_active_now = end_date_isnull and end_cycle_isnull

        # total_days
        if self.start_date and self.end_date:
            self.total_days = (self.end_date - self.start_date).days + 1
        else:
            self.total_days = 0

        # total_cycle
        if (self.start_date and self.end_date and self.start_cycle and self.end_cycle):
            delta_days = (self.end_date - self.start_date).days
            start_cycle_num = int(self.start_cycle)
            end_cycle_num = int(self.end_cycle)
            self.total_cycle = delta_days * 2 + end_cycle_num - (start_cycle_num - 1)
        else:
            self.total_cycle = 0

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _('Projects')
        verbose_name_plural = _('Projects')

        indexes = [
            models.Index(fields=['company_name']),
            models.Index(fields=['location_name']),
            models.Index(fields=['is_active_now']),
            models.Index(fields=['company_name', 'location_name']),
        ]
        # Constraint ->  یعنی محدودیت دیتابیسی که مستقیم روی جدول در دیتابیس enforce میشه(نه فقط در کد جنگو)
        constraints = [
            models.CheckConstraint(
                name='end_not_befor_start',
                check=Q(end_date__isnull=True) | Q(end_date__gte=F('start_date')),
            ),
            # Q -> وقتی بخوایم شرطی رو  بسازیم
            # F -> ارجاع به مقدار یک فیلد دیگه در همان رکورد
            models.CheckConstraint(
                name='end_date_cycle_pair_nullity',
                check=(Q(end_date__isnull=True, end_cycle__isnull=True) |
                       Q(end_date__isnull=False, end_cycle__isnull=False)),
            ),
            models.CheckConstraint(
                name='end_cycle_gte_start_cycle_same_day',
                check=(Q(end_date__isnull=True) |
                       Q(end_cycle__isnull=True) |
                       ~Q(end_date=F('start_date')) |
                       Q(end_cycle__gte=F('start_cycle'))),
            )
        ]

    def __str__(self) -> str:
        return f"{self.company_name} - {self.location_name} - {self.start_date} - {self.end_date}"

