from django.contrib import admin
from .models import TimeRecord


@admin.register(TimeRecord)
class TimeRecordAdmin(admin.ModelAdmin):
    list_display = ['id', 'employee', 'date', 'clock_in_time', 'clock_out_time', 'get_hours']
    list_filter = ['date']
    search_fields = ['employee__first_name', 'employee__last_name']

    def get_hours(self, obj):
        return obj.calculate_hours()

    get_hours.short_description = 'Години'