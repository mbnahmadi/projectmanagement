from audioop import add
from django.contrib import admin
from import_export.admin import ExportMixin, ExportActionMixin
from import_export import resources, fields
from .models import CompanyModel, DayFormatModel, ProjectModel, ProjectFormatModel, LocationModel
from .forms import LocationAdminForm
from feedbackapp.models import FeedBackModel, FeedBackResponseModel, FeedBackAttachmentModel
from rangefilter.filters import DateRangeFilter
from feedbackapp.filters import HasFeedBackFilter

from nested_admin import NestedTabularInline, NestedStackedInline, NestedModelAdmin

# Register your models here.
class ProjectResource(resources.ModelResource):
    company_name = fields.Field(column_name='company', attribute='company_name__name', readonly=True)
    description = fields.Field(column_name='description', attribute='description')
    start_date = fields.Field(column_name='start date', attribute='start_date')
    end_date = fields.Field(column_name='end date', attribute='end_date')
    location_name = fields.Field(column_name='location', attribute='location_name__name', readonly=True)
    start_cycle_display = fields.Field(column_name='start cycle', attribute='start_cycle', readonly=True)
    end_cycle_display = fields.Field(column_name='end cycle', attribute='end_cycle', readonly=True)
    days_format = fields.Field(column_name='day format', attribute='days_format__format_name', readonly=True)

    class Meta:
        model = ProjectModel
        fields = (
            'id', 'company_name', 'description', 'start_date',
            'end_date', 'total_days', 'location_name', 'start_cycle_display',
            'end_cycle_display', 'total_cycle', 'days_format',
        )
        export_order = (
            'id', 'company_name', 'description', 'start_date',
            'end_date', 'total_days', 'location_name', 'start_cycle_display',
            'end_cycle_display', 'total_cycle', 'days_format'
        )

# --------------- Nested feedback model admin -----------------
class FeedBackAttachmentInline(NestedStackedInline):
    model = FeedBackAttachmentModel
    extra = 1
    max_num = 10

class FeedBackResponseInline(NestedStackedInline):
    model = FeedBackResponseModel
    extra = 0
    max_num = 1

class FeedBackInline(NestedStackedInline):
    model = FeedBackModel
    inlines = [FeedBackAttachmentInline, FeedBackResponseInline]
    extra = 0
    max_num = 2

@admin.register(ProjectModel)
class projectModelAdmin(ExportActionMixin, ExportMixin, NestedModelAdmin):
    # form = ProjectAdminForm
    inlines = [FeedBackInline]
    resource_class = ProjectResource
    list_display = ('company_name', 'location_name', 'start_date', 'end_date', 'total_days', 'days_format', 'is_active_now', 'has_feedback')
    list_filter = ('company_name', 'location_name', HasFeedBackFilter, 'is_active_now')
    search_fields = ('company_name__name', 'start_date', 'end_date')
    readonly_fields = ('total_cycle', 'total_days', 'is_active_now')

    def has_feedback(self, obj):
        return obj.feedbacks.exists()
    has_feedback.boolean = True  
    has_feedback.short_description = "Feed back?"

# =========== Company model admin ===========
@admin.register(CompanyModel)
class CompanyModelAdmin(admin.ModelAdmin):
    list_display = ('name',)

# =========== Location model admin ===========
@admin.register(LocationModel)
class LocationModelAdmin(admin.ModelAdmin):
    form = LocationAdminForm
    list_display = ('name',) 

# =========== project format model admin ===========
@admin.register(DayFormatModel)
class DayFormatModelAdmin(admin.ModelAdmin):
    list_display = ('format_name',) 

# =========== project format model admin ===========
@admin.register(ProjectFormatModel)
class ProjectFormatModelAdmin(admin.ModelAdmin):
    list_display = ('name',) 
