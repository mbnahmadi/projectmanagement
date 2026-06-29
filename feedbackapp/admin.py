from django.contrib import admin
from django.contrib.admin import ModelAdmin
from .models import FeedBackModel, FeedBackResponseModel, FeedBackAttachmentModel
# Register your models here.

class FeedBackAttachmentInline(admin.StackedInline):
    model = FeedBackAttachmentModel
    extra = 1
    min_num = 0
    max_num = 10

class FeedBackResponseInline(admin.StackedInline):
    model = FeedBackResponseModel
    extra = 0
    max_num = 1

@admin.register(FeedBackModel)
class FeedBackAdmin(admin.ModelAdmin):
    inlines = [FeedBackAttachmentInline, FeedBackResponseInline]

    list_display = ['get_company_name', 'get_location', 'get_start_date', 'get_end_date', 'through', 'date']
    # list_filter = ['get_company_name', 'get_location', 'date']

    def get_company_name(self, obj):
        return obj.project.company_name
    get_company_name.short_description = 'company'

    def get_location(self, obj):
        return obj.project.location
    get_location.short_description = 'location'
    
    def get_start_date(self, obj):
        return obj.project.location
    get_start_date.short_description = 'start_date'

    def get_end_date(self, obj):
        return obj.project.location
    get_end_date.short_description = 'end_date'

@admin.register(FeedBackResponseModel)
class FeedBackResponseAdmin(admin.ModelAdmin):
    list_display = ['get_company_name', 'get_location', 'through', 'date']
    # list_filter = ['get_company_name', 'get_location', 'date']

    def get_company_name(self, obj):
        return obj.feedback.project.company_name
    get_company_name.short_description = 'company'

    def get_location(self, obj):
        return obj.feedback.project.location
    get_location.short_description = 'location'