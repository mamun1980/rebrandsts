import json
from django.db.models import Max
from django.core.cache import cache
from django.shortcuts import render
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.contrib import admin
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View, ListView, CreateView, DetailView, UpdateView, DeleteView

from apps.amenities.models import AmenityTypeCategory, PartnerAmenityType
from apps.partners.models import Partner
from core.utils import Utils


class AmenityTypeListView(LoginRequiredMixin, ListView):
    template_name = 'generic_views/list_view.html'
    model = AmenityTypeCategory
    paginate_by = 10
    ordering = ['id']
    utils = Utils()

    def paginate_queryset(self, queryset, page_size):

        page_number = self.request.GET.get('page', '1')
        return self.utils.paginate_by_chunk_size_or_page_number(
            queryset, chunk_size=page_size, page_number=int(page_number)
        )

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['list_title'] = 'LeftTravel Amenity Type List'
        context['button_urls'] = ['add-amenity-type']
        return context


class AmenityTypeCreateView(LoginRequiredMixin, CreateView):
    template_name = 'generic_views/add_item_view.html'
    model = AmenityTypeCategory
    fields = ['name', 'partner_amenity_type']
    success_url = reverse_lazy("amenity-type-list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'LeftTravel Amenity Type CreateView'
        return context

    def form_valid(self, form):
        latest_id = AmenityTypeCategory.objects.aggregate(Max('id'))['id__max']
        form.instance.id = latest_id + 1 if latest_id else 1
        return super().form_valid(form)


class AmenityTypeUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'generic_views/update_form.html'
    model = AmenityTypeCategory
    fields = ['name', 'partner_amenity_type']
    success_url = reverse_lazy("amenity-type-list")

    def get_success_url(self):
        return self.request.path_info

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'LeftTravel Amenity Type UpdateView'
        return context


class AmenityTypeDetailView(LoginRequiredMixin, DetailView):
    template_name = 'generic_views/details_view.html'
    model = AmenityTypeCategory

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'LeftTravel Amenity Type DetailView'
        return context


class AmenityTypeDeleteView(LoginRequiredMixin, DeleteView):
    model = AmenityTypeCategory
    success_url = reverse_lazy("amenity-type-list")


class PartnerAmenityTypeListView(LoginRequiredMixin, ListView):
    template_name = 'generic_views/list_view.html'
    model = PartnerAmenityType
    paginate_by = 10
    ordering = ['id']
    utils = Utils()

    def paginate_queryset(self, queryset, page_size):

        page_number = self.request.GET.get('page', '1')
        return self.utils.paginate_by_chunk_size_or_page_number(
            queryset, chunk_size=page_size, page_number=int(page_number)
        )

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['list_title'] = 'Partner Amenity Type List'
        context['button_urls'] = ['add-partner-amenity-type']
        return context


class PartnerAmenityCreateView(LoginRequiredMixin, CreateView):
    template_name = 'generic_views/add_item_view.html'
    model = PartnerAmenityType
    fields = ['name', 'partner']
    success_url = reverse_lazy('add-partner-amenity-type')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Partner Amenity Type CreateView'
        return context

    def form_valid(self, form):
        latest_id = PartnerAmenityType.objects.aggregate(Max('id'))['id__max']
        form.instance.id = latest_id + 1 if latest_id else 1
        return super().form_valid(form)


class PartnerAmenityUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'generic_views/update_form.html'
    model = PartnerAmenityType
    fields = ['name', 'partner']

    def get_success_url(self):
        return self.request.path_info

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Partner Amenity Type UpdateView'
        return context


class PartnerAmenityDetailView(LoginRequiredMixin, DetailView):
    template_name = 'generic_views/details_view.html'
    model = PartnerAmenityType

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Partner Amenity Type DetailView'
        return context


class PartnerAmenityDeleteView(LoginRequiredMixin, DeleteView):
    model = PartnerAmenityType
    success_url = reverse_lazy("partner-amenity-type-list")


class AmenityTypeMappingView(LoginRequiredMixin, View):
    # template_name = 'amenities/drag_and_drop_amenity_mapping.html'
    template_name = 'admin/amenity_drag_and_drop.html'
    cache_time_out = 30  # cache out time: 0.5m

    def get(self, request, *args, **kwargs):
        # partners feed key list
        partners_list = [
            "BC", "HC", "VRBO", "FW", "HL", "AB", "AT", "EP", "LT",
            "HA", "HAUK", "HAAU", "HAES", "TA", "HG", "KY", "TC", "HP"
        ]

        # Getting from redis
        partners = cache.get('partners')
        lefttravel_amenity_type = cache.get('lefttravel_amenity_type')

        # Getting from DB
        if not partners and not lefttravel_amenity_type:
            partners = Partner.objects.filter(key__in=partners_list)
            # partners = Partner.objects.distinct().order_by('name')
            cache.set('partners', partners, self.cache_time_out)

            lefttravel_amenity_type = AmenityTypeCategory.objects.order_by('name')
            cache.set('lefttravel_amenity_type', lefttravel_amenity_type, self.cache_time_out)

        partner_amenity_list_in_lefttravel = set()
        partner_amenity_obj_list = [atc.partner_amenity_type.all() for atc in lefttravel_amenity_type]
        for obj in partner_amenity_obj_list:
            obj_list = [i.id for i in obj]
            partner_amenity_list_in_lefttravel.update(obj_list)
        # getting from redis
        partner_amenity_type = cache.get('partner_amenity_type')
        if partner_amenity_type is None:
            partner_amenity_type = PartnerAmenityType.objects.exclude(
                id__in=[item for item in partner_amenity_list_in_lefttravel]
            )
            cache.set('partner_amenity_type', partner_amenity_type, self.cache_time_out)

        admin_context = dict(
            admin.site.each_context(self.request)
        )
        context = {
            'partners': partners,
            'amenity_types': lefttravel_amenity_type,
            'partner_amenity_types': partner_amenity_type
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
        for key, items_list in data.items():
            if key.startswith('lefttravel-type'):
                exist_partner_property_type_obj = PartnerAmenityType.objects.filter(id__in=items_list)
                amenity_filter_obj = AmenityTypeCategory.objects.filter(
                    partner_amenity_type__in=exist_partner_property_type_obj
                )
                for amenity_type in amenity_filter_obj:
                    amenity_type.partner_amenity_type.remove(*exist_partner_property_type_obj)
            else:
                for items in items_list:
                    json_item = json.loads(items)
                    self.process_json_data_to_bulk_insert(json_item=json_item)

        response_data = {'message': 'Data received and processed successfully'}
        return JsonResponse(response_data)

    @staticmethod
    def process_json_data_to_bulk_insert(json_item: dict):
        try:
            for key, items in json_item.items():
                pam_objs = PartnerAmenityType.objects.filter(id__in=[int(item) for item in items])
                amenity_type_obj_list = AmenityTypeCategory.objects.order_by('id')
                amenity_type_obj = amenity_type_obj_list.get(id=int(key))
                for amenity_type_obj_item in amenity_type_obj_list:
                    for pam_obj in pam_objs:
                        amenity_type_obj_item.partner_amenity_type.remove(pam_obj)

                amenity_type_obj.partner_amenity_type.add(*[i for i in pam_objs])
                amenity_type_obj.save()
        except Exception as error:
            pass