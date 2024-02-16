from django.contrib import admin
from .models import VrsAnalytics


@admin.register(VrsAnalytics)
class VrsAnalyticsAdmin(admin.ModelAdmin):
    list_display = ['id', 'device', 'feed', 'site_key', 'country_code', 'transaction_date', 'predicted_revenue',
                    'partner']

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False
