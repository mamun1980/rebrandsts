from django.contrib import admin
from apps.amenities.models import AmenityTypeCategory, PartnerAmenityType


@admin.register(AmenityTypeCategory)
class AmenityTypeCategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'get_partner_amenity_type', 'create_date', 'update_date']
    list_display_links = ['id', 'name']
    search_fields = ['name', 'partner_amenity_type__name']
    readonly_fields = ['id']
    ordering = ['id', 'update_date']
    view_on_site = False


@admin.register(PartnerAmenityType)
class AmenityTypeCategoryAdmin(admin.ModelAdmin):
    list_display = [f.name for f in PartnerAmenityType._meta.fields]
    list_display_links = ['id', 'name']
    search_fields = ['name', 'partner__name']
    readonly_fields = ['id']
    view_on_site = False
    list_filter = ['partner__name']
    ordering = ['id', 'update_date']

