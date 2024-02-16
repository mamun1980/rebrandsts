from django.contrib import admin
from apps.brands.filters import BrandFilter
from apps.property.filters import PropertyGroupFilter
from apps.sts.filters import LocationFilter
from .forms import SetListESForm, SetListESNewForm
from .models import BrandLocationPartnerProperty, BrandLocationPartnerPropertyProvider, SQSTerms, \
    SetList, SiteEnableSets, SetListES, SiteEnableSetsES


@admin.register(BrandLocationPartnerProperty)
class BrandLocationPartnerPropertyAdmin(admin.ModelAdmin):
    list_display = ['id', 'brand', 'location', 'device', 'property_group', 'kayak_provider_ordering']
    # list_filter = ['device', BrandFilter, LocationFilter, PropertyGroupFilter, ]
    search_fields = ['brand', 'device', 'property_group', 'location']
    ordering = ['id']
    readonly_fields = ['id']

    def save_model(self, request, obj, form, change):
        obj.created_by = request.user
        # if not obj.id:
        #     latest_id = BrandLocationPartnerProperty.objects.aggregate(Max('id'))['id__max']
        #     obj.id = latest_id + 1
        super().save_model(request, obj, form, change)

    def kayak_provider_ordering(self, obj):
        providers = obj.brandlocationpartnerpropertyprovider_set.all().order_by('order')
        provider_name_list = [p.provider.provider_id for p in providers]
        return provider_name_list


@admin.register(BrandLocationPartnerPropertyProvider)
class BrandLocationPartnerPropertyProviderAdmin(admin.ModelAdmin):
    list_display = ['brand_name', 'user_location', 'device_type', 'property_group', 'provider', 'order', 'status']
    list_filter = ['loc__device', 'loc__property_group', 'loc__location']
    list_editable = ('order',)
    search_fields = ['loc__id']
    ordering = ['order']
    readonly_fields = ['id']

    def save_model(self, request, obj, form, change):
        obj.created_by = request.user
        # if not obj.id:
        #     latest_id = BrandLocationPartnerPropertyProvider.objects.aggregate(Max('id'))['id__max']
        #     obj.id = latest_id + 1
        super().save_model(request, obj, form, change)

    def brand_name(self, obj):
        return obj.loc.brand.name

    def user_location(self, obj):
        return obj.loc.location.country

    def device_type(self, obj):
        return obj.loc.device.type

    def property_group(self, obj):
        return obj.loc.property_group


@admin.register(SQSTerms)
class SQSTermsAdmin(admin.ModelAdmin):
    list_display = ['id', 'keyword', 'brand_type']
    list_filter = ['brand_type']
    readonly_fields = ['id']

    def save_model(self, request, obj, form, change):
        obj.created_by = request.user
        # if not obj.id:
        #     latest_id = SQSTerms.objects.aggregate(Max('id'))['id__max']
        #     obj.id = latest_id + 1
        super().save_model(request, obj, form, change)


# @admin.register(SetList)
# class SetListAdmin(admin.ModelAdmin):
#     list_display = ['id', 'name', 'description', 'solr_fields', 'default', 'created_at', 'updated_at']
#     ordering = ['id']
#
#
# @admin.register(SiteEnableSets)
# class SiteEnableSetsAdmin(admin.ModelAdmin):
#     list_display = ['id', 'set_list', 'site', 'show_site', 'active', 'created_at', 'updated_at']
#     list_filter = ['set_list']
#     ordering = ['id']
#
#     def show_site(self, obj):
#         return obj.site.key


@admin.register(SetListES)
class SetListESAdmin(admin.ModelAdmin):
    form = SetListESForm
    list_display = ['id', 'name', 'description', 'default', 'index_name', 'created_at', 'updated_at']
    search_fields = ['name']
    ordering = ['id']
    readonly_fields = ['id']

    def save_model(self, request, obj, form, change):
        obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(SiteEnableSetsES)
class SiteEnableSetsESAdmin(admin.ModelAdmin):
    list_display = ['id', 'set_list', 'show_brands', 'show_sites', 'active', 'created_at', 'updated_at']
    list_filter = ['active', 'set_list']
    ordering = ['id']
    readonly_fields = ['id']

    def save_model(self, request, obj, form, change):
        obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def show_sites(self, obj):
        brands = obj.brands.all()
        sites = ", ".join([brand.key for brand in brands])
        return sites