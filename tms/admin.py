from django.contrib import admin

from .models import ClockItem
from cms.models import Photo


# Register your models here.
class ClockItemAdmin(admin.ModelAdmin):
    list_display = ['thing', 'start_time', 'end_time', 'time_cost_min', 'category', 'project']
    list_filter = ['year', 'category', 'project', 'start_hour']


class PhotoAdmin(admin.ModelAdmin):
    list_display = ['uri', 'taken_time', 'address', 'camera']
    list_filter = ['taken_time', 'city', 'camera', 'lens', 'focal_length', 'f_number', 'iso']


admin.site.register(ClockItem, ClockItemAdmin)
admin.site.register(Photo, PhotoAdmin)
