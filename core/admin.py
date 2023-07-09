from django.contrib import admin
from .models import *

@admin.register(Link)
class LinkAdmin(admin.ModelAdmin):
    list_display = ['base_url', 'short_url', 'last_usage', 'usage_count']
    
@admin.register(usageChart)
class usageChartAdmin(admin.ModelAdmin):
    list_display = ['url', 'usage_time']
    readonly_fields = ['url']