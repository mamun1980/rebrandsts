from django.contrib import admin
from apps.partners.filters import PartnerFilter
from django.db.models import Max
from .filters import BrandFilter
from .models import Brand, BrandsPartners, BrandsProviders, StaticSiteMapUrl, DynamicSiteMapUrl


class BrandsPartnerInline(admin.StackedInline):
    model = BrandsPartners
    list_display = ['partner']
    extra = 1


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'key', 'sort_order', 'alias', 'show_partners', 'date']
    search_fields = ['name', 'key', 'alias']
    readonly_fields = ['id']
    ordering = ['-updated_at', 'id']
    inlines = [BrandsPartnerInline]
    view_on_site = False

    def save_model(self, request, obj, form, change):
        obj.created_by = request.user
        # if not obj.id:
            # latest_id = Brand.objects.aggregate(Max('id'))['id__max']
            # obj.id = latest_id + 1 if latest_id else 1
        super().save_model(request, obj, form, change)

    def show_partners(self, obj):
        partners = obj.get_partners()
        names = [p.partner.name for p in partners]
        return ', '.join(names)


@admin.register(BrandsPartners)
class BrandsPartnersAdmin(admin.ModelAdmin):
    model = BrandsPartners
    list_display = ['brand', 'partner']
    # list_filter = [BrandFilter, PartnerFilter]


@admin.register(BrandsProviders)
class BrandsProvidersAdmin(admin.ModelAdmin):
    list_display = ['brand', 'provider']
