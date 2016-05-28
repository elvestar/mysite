from django.contrib import admin

from .models import ClockItem


# Register your models here.
class ClockItemAdmin(admin.ModelAdmin):
    list_display = ['thing', 'start_time', 'end_time', 'time_cost_min', 'category', 'project']
    list_filter = ['year', 'category', 'project', 'start_hour']

admin.site.register(ClockItem, ClockItemAdmin)
