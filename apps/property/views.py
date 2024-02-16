import json
from django.contrib import admin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, UpdateView, View
from django.views.generic.edit import CreateView, DeleteView
from django.db.models import Max
from apps.partners.models import Partner
from .models import PropertyType, PartnerPropertyType, PartnerPropertyMapping
from .forms import PartnerPropertyMappingForm, PropertyTypeForm, PartnerPropertyTypeForm
from django.shortcuts import render
from core.utils import Utils
from core.service import CoreService
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.core.cache import cache


class PropertyTypeListView(LoginRequiredMixin, ListView):
    template_name = 'property/property_types_list.html'
    model = PropertyType
    paginate_by = 10
    ordering = ['-create_date']
    utils = Utils()

    def paginate_queryset(self, queryset, page_size):

        page_number = self.request.GET.get('page', '1')
        return self.utils.paginate_by_chunk_size_or_page_number(
            queryset, chunk_size=page_size, page_number=int(page_number)
        )


class PropertyTypeDetailsView(LoginRequiredMixin, DetailView):
    template_name = 'property/property_types_details.html'
    model = PropertyType


class PropertyTypeCreateView(LoginRequiredMixin, CreateView):
    template_name = 'property/property_types_add.html'
    model = PropertyType
    form_class = PropertyTypeForm
    success_url = '/property-types/'

    def form_valid(self, form):
        # latest_id = PropertyType.objects.aggregate(Max('id'))['id__max']
        # form.instance.id = latest_id + 1 if latest_id else 1
        return super().form_valid(form)


class PropertyTypeUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'property/propertytype_form.html'
    model = PropertyType
    form_class = PropertyTypeForm
    success_url = '/property-types/'


class PropertyTypeDeleteView(LoginRequiredMixin, DeleteView):
    model = PropertyType
    success_url = "/property-types/"


class PartnerPropertyTypeListView(LoginRequiredMixin, ListView):
    template_name = 'property/partner_property_types_list.html'
    model = PartnerPropertyType
    paginate_by = 10
    ordering = ['-create_date']
    utils = Utils()

    def paginate_queryset(self, queryset, page_size):

        page_number = self.request.GET.get('page', '1')
        return self.utils.paginate_by_chunk_size_or_page_number(
            queryset, chunk_size=page_size, page_number=int(page_number)
        )


class PartnerPropertyTypeDetailsView(LoginRequiredMixin, DetailView):
    template_name = 'property/partner_property_types_details.html'
    model = PartnerPropertyType


class PartnerPropertyTypeCreateView(LoginRequiredMixin, CreateView):
    template_name = 'property/partner_property_types_add.html'
    model = PartnerPropertyType
    form_class = PartnerPropertyTypeForm
    success_url = "/partner-property-types/"

    def form_valid(self, form):
        # latest_id = PartnerPropertyType.objects.aggregate(Max('id'))['id__max']
        # form.instance.id = latest_id + 1 if latest_id else 1
        return super().form_valid(form)


class PartnerPropertyTypeUpdateView(LoginRequiredMixin, UpdateView):
    model = PartnerPropertyType
    form_class = PartnerPropertyTypeForm
    success_url = "/partner-property-types/"


class PartnerPropertyTypeDeleteView(LoginRequiredMixin, DeleteView):
    model = PartnerPropertyType
    success_url = "/partner-property-types/"


class PartnerPropertyMappingListView(LoginRequiredMixin, ListView):
    template_name = 'property/partner_property_mapping_list.html'
    model = PartnerPropertyMapping
    paginate_by = 10
    utils = Utils()

    def get_queryset(self):
        qs = PartnerPropertyMapping.objects.all().order_by('property_type__create_date')

        partner_id = self.request.GET.get('partner')
        if partner_id:
            qs = qs.filter(
                partner_property__partner=partner_id
            )
        
        pt_id = self.request.GET.get('property')
        if pt_id:
            qs = qs.filter(
                property_type=pt_id
            )

        return qs

    def paginate_queryset(self, queryset, page_size):

        page_number = self.request.GET.get('page', '1')
        return self.utils.paginate_by_chunk_size_or_page_number(
            queryset, chunk_size=page_size, page_number=int(page_number)
        )

    def get_context_data(self, **kwargs):
        context = super(PartnerPropertyMappingListView, self).get_context_data(**kwargs)
        context['partners'] = Partner.objects.all()
        context['properties'] = PropertyType.objects.all()
        return context


class PartnerPropertyMappingCreateView(LoginRequiredMixin, CreateView):
    template_name = 'property/partner_property_mapping_add.html'
    model = PartnerPropertyMapping
    fields = ['property_type', 'partner_property']

    def form_valid(self, form):
        # latest_id = PartnerPropertyMapping.objects.aggregate(Max('id'))['id__max']
        # form.instance.id = latest_id + 1
        return super().form_valid(form)


class PartnerPropertyMappingDetailsView(LoginRequiredMixin, DetailView):
    template_name = 'property/partner_property_mapping_details.html'
    model = PartnerPropertyMapping

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ppm = kwargs['object']
        pt = ppm.property_type
        ppts_all = pt.partnerpropertymapping_set.all()
        properties_mappings = {}
        for ppt in ppts_all:
            if ppt.partner_property.partner in properties_mappings.keys():
                properties_mappings[ppt.partner_property.partner].append({ppt.id: ppt.partner_property.name})
            else:
                properties_mappings[ppt.partner_property.partner] = [{ppt.id: ppt.partner_property.name}]

        context['partner_properties'] = properties_mappings
        context['ppt_form'] = PartnerPropertyMappingForm
        return context


class PartnerPropertyMappingDeleteView(LoginRequiredMixin, DeleteView):
    model = PartnerPropertyMapping
    success_url = "/partner-property-mappings/"


class DragAndDropPartnerPropertyMappingView(LoginRequiredMixin, View):
    utils = Utils()
    core_service = CoreService()
    # template_name = 'property/drag_and_drop_partner_property_mapping.html'
    template_name = 'admin/property_drag_and_drop.html'
    cache_time_out = 30  # cache out time: 0.5m

    def get(self, request):
        # ignore_partners by id
        ignore_partners_list = [2, 7, 6, 8, 9, 10, 11, 15, 17, 18]
        # Getting data from redis
        partners = cache.get('property_partners')
        property_type = cache.get('property_property_type')
        partner_property_mapping = cache.get('property_partner_property_mapping')

        if not partners and not property_type and not partner_property_mapping:
            # partners = Partner.objects.all().distinct().order_by('name')
            partners = Partner.objects.exclude(id__in=ignore_partners_list).order_by('name')
            property_type = PropertyType.objects.order_by('name')
            partner_property_mapping = PartnerPropertyMapping.objects.order_by('pk')
            # Setting data to redis
            cache.set('property_partners', partners, self.cache_time_out)
            cache.set('property_property_type', property_type, self.cache_time_out)
            cache.set('property_partner_property_mapping', partner_property_mapping, self.cache_time_out)

        partner_property_mapping_id_list = [mapping.partner_property.id for mapping in partner_property_mapping]
        # Getting data from redis
        partner_property_type = cache.get('property_partner_property_type')
        if partner_property_type is None:
            partner_property_type = PartnerPropertyType.objects.exclude(
                id__in=partner_property_mapping_id_list
            ).order_by('update_date')
            # Setting partner_property_type into redis
            cache.set('property_partner_property_type', partner_property_type, self.cache_time_out)
        admin_context = dict(
            admin.site.each_context(self.request)
        )
        context = {
            'partners': partners,
            'property_types': property_type,
            'partner_property_types': partner_property_type,
            'partner_property_mapping': partner_property_mapping
        }
        context.update(admin_context)
        return render(request, self.template_name, context)

    @csrf_exempt
    def post(self, request, *args, **kwargs):
        request_json = request.POST.get('message')
        if not request_json:
            response_data = {'error': 'This is not a valid request.'}
            return JsonResponse(response_data, status=400)

        data = json.loads(request_json)
        ppm_objs_to_create = []
        for key, items_list in data.items():
            if key.startswith('lefttravel-type'):
                exist_partner_property_type_mapping_obj = PartnerPropertyMapping.objects.filter(
                    partner_property__id__in=items_list
                )
                delete_obj = exist_partner_property_type_mapping_obj.delete()
            else:
                for items in items_list:
                    json_item = json.loads(items)
                    self.process_json_data_to_bulk_insert(
                        json_item=json_item, partner_property_mapping_empty_list=ppm_objs_to_create
                    )

        if ppm_objs_to_create:
            insert = self.core_service.bulk_insert(model=PartnerPropertyMapping, obj_list=ppm_objs_to_create)
            print(insert)

        response_data = {'message': 'Data received and processed successfully'}
        return JsonResponse(response_data)

    @staticmethod
    def process_json_data_to_bulk_insert(json_item: dict, partner_property_mapping_empty_list: list):
        try:
            for keys, item in json_item.items():
                property_type_obj = PropertyType.objects.get(id=int(keys))
                ppm_objs = PartnerPropertyType.objects.filter(id__in=item)
                existing_mapping_ids = PartnerPropertyMapping.objects.filter(
                    partner_property__id__in=ppm_objs
                ).values_list('partner_property__id', flat=True)

                for ppm_obj in ppm_objs:
                    if ppm_obj.id not in existing_mapping_ids:
                        property_mapping = PartnerPropertyMapping(
                            property_type=property_type_obj, partner_property=ppm_obj
                        )
                        partner_property_mapping_empty_list.append(property_mapping)
        except Exception as error:
            pass
