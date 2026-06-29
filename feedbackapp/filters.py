from django.contrib.admin import SimpleListFilter

class HasFeedBackFilter(SimpleListFilter):
    title = 'feedback'
    parameter_name = 'has_feedback'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Yes'),
            ('no', 'No'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(feedbacks__isnull=False).distinct()
        if self.value() == 'no':
            return queryset.filter(feedbacks__isnull=True)
        return queryset