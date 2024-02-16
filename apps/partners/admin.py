from django.contrib import admin
from django.db.models import Max
from .filters import PartnerFilter
from .models import Partner, Provider, PartnerProvider


class ProviderInline(admin.StackedInline):
    model = PartnerProvider
    extra = 1


class ProviderAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'provider_id']
    ordering = ['id']


admin.site.register(Provider, ProviderAdmin)


@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    inlines = [ProviderInline]
    model = Partner
    list_display = ['id', 'name', 'key', 'domain_name', 'feed', 'date']
    search_fields = ['name', 'key', 'domain_name', 'feed']
    ordering = ['sort_order']
    readonly_fields = ['id']
    view_on_site = False

    def save_model(self, request, obj, form, change):
        obj.created_by = request.user
        # if not obj.id:
        #     latest_id = Partner.objects.aggregate(Max('id'))['id__max']
        #     obj.id = latest_id + 1
        super().save_model(request, obj, form, change)


# @admin.register(PartnerProvider)
# class PartnerProviderAdmin(admin.ModelAdmin):
#     list_display = ['provider_name', 'provider_id', 'date', 'order', 'is_active']
#     list_filter = ['is_active', 'partner']
#     ordering = ['order']
#
#     def provider_name(self, obj):
#         return obj.provider.name
#
#     def provider_id(self, obj):
#         return obj.provider.provider_id


@admin.register(PartnerProvider)
class KayakProviderAdmin(admin.ModelAdmin):
    verbose_name = "Kayak Provider"  # Singular display name
    verbose_name_plural = "Kayak Provider"  # Plural display name
    list_display = ['provider_name', 'provider_id', 'date', 'order', 'is_active']
    list_filter = ['is_active', PartnerFilter]
    ordering = ['order']

    def provider_name(self, obj):
        return obj.provider.name

    def provider_id(self, obj):
        return obj.provider.provider_id
