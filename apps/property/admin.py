from django.contrib import admin
from django.db.models import Max
from apps.partners.filters import PartnerFilter
from .models import PropertyGroup, PropertyCategory, PropertyType, PartnerPropertyType, \
    PartnerPropertyMapping


@admin.register(PropertyGroup)
class PropertyGroupAdmin(admin.ModelAdmin):
    add_form_template = 'admin/property_group_add_form.html'
    change_form_template = 'admin/property_group_change_form.html'
    list_display = ['id', 'name', 'property_ordering', 'property_type_set', 'create_date', 'update_date']
    search_fields = ['name']
    ordering = ['property_ordering']
    readonly_fields = ['id']

    def add_view(self, request, form_url="", extra_context=None):
        extra_context = extra_context or {}
        extra_context['property_types'] = PropertyType.objects.all()
        return super(PropertyGroupAdmin, self).add_view(request, form_url=form_url, extra_context=extra_context)
    
    def change_view(self, request, object_id, form_url="", extra_context=None):
        extra_context = extra_context or {}
        pg = PropertyGroup.objects.get(id=object_id)
        extra_context["form"] = self.get_form(request, obj=pg)
        extra_context['property_types'] = PropertyType.objects.all()
        extra_context['property_type_sets'] = pg.property_type_sets
        return super(PropertyGroupAdmin, self).change_view(request, object_id, form_url=form_url, extra_context=extra_context)

    def save_model(self, request, obj, form, change):
        pts = request.POST.getlist('property_types')
        obj.created_by = request.user
        # if not obj.id:
        #     latest_id = PropertyGroup.objects.aggregate(Max('id'))['id__max']
        #     obj.id = latest_id + 1 if latest_id else 1
        obj.save()

        ptypes = obj.propertytype_set.all()
        post_ptypes = PropertyType.objects.filter(id__in=pts)
        if ptypes:
            new_ptypes = post_ptypes.difference(ptypes)
            removed_ptypes = ptypes.difference(post_ptypes)
            unchanged_ptypes = post_ptypes.distinct(ptypes)
        
            for pt in new_ptypes:
                obj.propertytype_set.add(pt)
            
            for pt in removed_ptypes:
                obj.propertytype_set.remove(pt)
        else:
            for pt in post_ptypes:
                obj.propertytype_set.add(pt)

        super().save_model(request, obj, form, change)

    def sqs_terms(self, obj):
        types = obj.propertytype_set.all()
        ids =[str(v.id) for v in types]
        id_str = ','.join(ids)
        return f"{id_str}"

    def property_type_set(self, obj):
        pts = obj.propertytype_set.all()
        ids =[str(v.name) for v in pts]
        id_str = ','.join(ids)
        return id_str


@admin.register(PartnerPropertyType)
class PartnerPropertyTypeAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'partner', 'create_date']
    # list_filter = [PartnerFilter]
    readonly_fields = ['id']
    view_on_site = False

    def save_model(self, request, obj, form, change):
        obj.created_by = request.user
        # if not obj.id:
        #     latest_id = PropertyType.objects.aggregate(Max('id'))['id__max']
        #     obj.id = latest_id + 1 if latest_id else 1
        super().save_model(request, obj, form, change)


@admin.register(PropertyType)
class PropertyTypeAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'brand_type', 'create_date', 'update_date']
    search_fields = ['name']
    list_filter = ['brand_type']
    ordering = ['id']
    readonly_fields = ['id']
    view_on_site = False

    def save_model(self, request, obj, form, change):
        obj.created_by = request.user
        # if not obj.id:
        #     latest_id = PropertyType.objects.aggregate(Max('id'))['id__max']
        #     obj.id = latest_id + 1 if latest_id else 1
        super().save_model(request, obj, form, change)


@admin.register(PartnerPropertyMapping)
class PartnerPropertyMappingAdmin(admin.ModelAdmin):
    list_display = ['property_name', 'partner_property_name']
    list_filter = ['partner_property__partner', 'property_type__name']
    view_on_site = False

    def property_name(self, obj):
        return obj.property_type.name

    def partner_property_name(self, obj):
        return obj.partner_property.name


admin.site.register(PropertyCategory)
