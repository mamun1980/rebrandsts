import datetime, time
import json
from functools import partial
import concurrent.futures
from django.utils import timezone
import subprocess
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.contrib import messages
from decouple import config
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, TemplateView, UpdateView
from django.views.generic.edit import CreateView, DeleteView
from django.db.models import Max
from django.http import JsonResponse
from api import BASE_STS_PATH
from api.services import STSAPIService
from apps.partners.models import Partner
from apps.property.models import PropertyGroup
from apps.brands.models import Brand
from core.service import CoreService
from core.utils import Utils
from .models import (BrandLocationDefinedSetsRatio, Device, Location, SearchLocation, RatioSet, PartnerRatio)
from .forms import (BrandLocationDefinedSetsRatioBulkInsertForm, SearchLocationForm, RatioSetForm, LocationForm,
                    BrandLocationDefinedSetsRatioForm)
from .service.s3_service import S3Services
from .tasks import perform_bulk_update_task
from core.utils import Utils


@csrf_exempt
def invalidate_cache_and_recache(request, site_key):
    print(request.method)
    print(f"Site Key: {site_key}")
    if request.method == 'POST':
        site_key = site_key.strip()
        utils = Utils()
        ratio_service = STSAPIService()
        core_service = CoreService()
        s3_service = S3Services()
        bucket_name = config('S3_BUCKET_NAME')
        s3_config = core_service.s3_config()
        s3_client = core_service.s3_connection(s3_config)
        site_env = config('SITE_ENV', 'dev')
        try:
            data = ratio_service.get_ratio(site_key.upper())
            data['updated_at'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            site_key = site_key.lower()
            file_location = f"{BASE_STS_PATH}{site_key}.json"
            utils.remove_files(BASE_STS_PATH, f"{site_key}.json")
            utils.write_json_file(data=data, file_location=file_location)
            s3_object_name = f"{site_env}/{site_key}.json"
            s3_service.s3_file_process(bucket_name, file_location, s3_object_name, s3_client)
        except Exception as err:
            print(err)
        data = {"message": "Success", "site_key": site_key}
        return JsonResponse(data, status=200)


class BulkActionsView(LoginRequiredMixin, TemplateView):

    def get(self, request, *args, **kwargs):
        selected_object_ids = request.GET.getlist('brand_location_ratio_set_ids', [])
        if not selected_object_ids:
            messages.warning(request, "No item selected!")
            return redirect('sts:brand-location-ratio-set-list')
        action = request.GET.get('submit')
        if action == 'bulk_update':
            selected_objects = BrandLocationDefinedSetsRatio.objects.filter(id__in=selected_object_ids)
            partners = Partner.objects.all()
            devices = Device.objects.all()
            locations = Location.objects.all()
            accommodation_types = PropertyGroup.objects.all()
            search_locations = SearchLocation.objects.all()
            context = {
                'selected_objects': selected_objects, 'partners': partners,
                'devices': devices, 'accommodation_types': accommodation_types,
                'locations': locations, 'search_locations': search_locations
            }
            return render(request, 'sts/confirm_bulk_update.html', context)
        else:
            return render(request, 'sts/bulk_clone_ratio_sets.html')


def confirm_bulk_update(request):
    selected_object_ids = request.session.pop('selected_object_ids', [])
    if not selected_object_ids:
        return HttpResponseRedirect('/sts/brandlocationdefinedsetsratio/')
    selected_objects = BrandLocationDefinedSetsRatio.objects.filter(id__in=selected_object_ids)
    partners = Partner.objects.all()
    devices = Device.objects.all()
    locations = Location.objects.all()
    accommodation_types = PropertyGroup.objects.all()
    search_locations = SearchLocation.objects.all()
    context = {
        'selected_objects': selected_object_ids, 'partners': partners,
        'devices': devices, 'accommodation_types': accommodation_types,
        'locations': locations, 'search_locations': search_locations
    }
    return render(request, 'admin/sts/confirm_bulk_update.html', context)


def perform_bulk_update(request):
    action = request.POST.get('action')
    if request.method == 'POST' and 'action' in request.POST:
        partner_ratios_ids = request.POST.getlist('partner_ratios')
        partner_ids = request.POST.getlist('partner_ids')
        selected_object_ids = request.POST.getlist('selected_objects')

        # perform_bulk_update_task(ratio_set_title, partner_ratios_ids, partner_ids, selected_object_ids)
        arg_data = (f"--partner_ratios_ids '{partner_ratios_ids}'"
                    f" --partner_ids '{partner_ids}' --selected_object_ids '{selected_object_ids}'")

        try:
            django_command = f'python manage.py perform_bulk_update {arg_data}'
            subprocess.Popen(
                django_command,
                shell=True,
                text=True,
            )
        except Exception as err:
            print(f'Sub process running err: {err}')

        messages.success(request, f"Bulk update is in progress ...")

        if action == 'confirm_admin_action':
            return HttpResponseRedirect('/sts/brandlocationdefinedsetsratio/')
        else:
            return redirect('sts:brand-location-ratio-set-list')


def bulk_clone_ratio_set_view(request):
    if not request.user.is_authenticated:
        return redirect('/accounts/login/')
    if request.method == 'POST':
        ratio_set_ids = request.POST.getlist('ratio_set_ids')
        brand_id_list = request.POST.getlist('brands')
        brand_list = Brand.objects.filter(id__in=brand_id_list)
        ratio_set_list = BrandLocationDefinedSetsRatio.objects.filter(id__in=ratio_set_ids)
        latest_id = BrandLocationDefinedSetsRatio.objects.aggregate(Max('id'))['id__max']

        new_ratio_sets = []
        for brand in brand_list:
            for ratio_set in ratio_set_list:
                is_exist = BrandLocationDefinedSetsRatio.objects.filter(
                    brand=brand,
                    location=ratio_set.location,
                    search_location=ratio_set.search_location,
                    device=ratio_set.device,
                    property_group=ratio_set.property_group
                ).exists()
                if not is_exist:
                    latest_id=latest_id+1
                    new_ratio_sets.append(
                        BrandLocationDefinedSetsRatio(
                            id=latest_id,
                            brand=brand,
                            location=ratio_set.location,
                            search_location=ratio_set.search_location,
                            device=ratio_set.device,
                            property_group=ratio_set.property_group,
                            ratio_set=ratio_set.ratio_set,
                            created_by=request.user,
                            created_at=timezone.now(),
                            updated_at=timezone.now()
                            
                        )
                    )
        BrandLocationDefinedSetsRatio.objects.bulk_create(new_ratio_sets)
    else:
        return render(request, 'sts/bulk_clone_ratio_sets.html')
        
    return HttpResponseRedirect('/admin/sts/brandlocationdefinedsetsratio/')


class LocationListView(LoginRequiredMixin, ListView):
    template_name = 'sts/location_list.html'
    model = Location
    paginate_by = 10
    ordering = ['-updated_at']


class LocationDetailsView(LoginRequiredMixin, DetailView):
    template_name = 'sts/location_details.html'
    model = Location


class LocationCreateView(LoginRequiredMixin, CreateView):
    template_name = 'sts/location_create.html'
    model = Location
    fields = ['location_type', 'country_code', 'country']

    def form_valid(self, form):
        # latest_id = Location.objects.aggregate(Max('id'))['id__max']
        # form.instance.id = latest_id + 1
        return super().form_valid(form)


class LocationUpdateView(LoginRequiredMixin, UpdateView):
    model = Location
    form_class = LocationForm
    success_url = '/locations/'


class LocationsDeleteView(LoginRequiredMixin, DeleteView):
    model = Location
    success_url = "/locations/"


class SearchLocationListView(LoginRequiredMixin, ListView):
    template_name = 'sts/search_location_list.html'
    model = SearchLocation
    paginate_by = 10
    ordering = ['-update_date']
    utils = Utils()

    def paginate_queryset(self, queryset, page_size):

        page_number = self.request.GET.get('page', '1')
        return self.utils.paginate_by_chunk_size_or_page_number(
            queryset, chunk_size=self.paginate_by, page_number=int(page_number)
        )


class SearchLocationDetailsView(LoginRequiredMixin, DetailView):
    template_name = 'sts/search_location_details.html'
    model = SearchLocation


class SearchLocationCreateView(LoginRequiredMixin, CreateView):
    template_name = 'sts/search_location_create.html'
    model = SearchLocation
    form_class = SearchLocationForm


class SearchLocationUpdateView(LoginRequiredMixin, UpdateView):
    model = SearchLocation
    form_class = SearchLocationForm
    success_url = "/search-locations/"


class SearchLocationsDeleteView(LoginRequiredMixin, DeleteView):
    model = SearchLocation
    success_url = "/search-locations/"


class RatioSetListView(LoginRequiredMixin, ListView):
    template_name = 'sts/ratio_set_list.html'
    model = RatioSet
    ordering = ['-created_at']
    paginate_by = 10


class RatioSetDetailsView(LoginRequiredMixin, DetailView):
    template_name = 'sts/ratio_set_details.html'
    model = RatioSet


class RatioSetCreateView(LoginRequiredMixin, CreateView):
    template_name = 'sts/ratio_set_create.html'
    model = RatioSet
    form_class = RatioSetForm

    def form_valid(self, form):
        ratio_set = form.save()
        data_dict = self.request.POST.dict()
        data_dict.pop('title')
        data_dict.pop('csrfmiddlewaretoken')
        data_dict.pop('ratio_location')
        for key, val in data_dict.items():
            if val != '':
                partner = Partner.objects.get(key=key)
                PartnerRatio.objects.create(
                    partner=partner,
                    ratio=val,
                    ratioset=ratio_set
                )

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(RatioSetCreateView, self).get_context_data(**kwargs)
        context['partners'] = Partner.objects.all()
        return context


class RatioSetUpdateView(LoginRequiredMixin, UpdateView):
    model = RatioSet
    form_class = RatioSetForm
    success_url ="/ratio-sets/"

    def form_valid(self, form):
        ratio_set = form.save()
        data_dict = self.request.POST.dict()
        data_dict.pop('title')
        data_dict.pop('csrfmiddlewaretoken')
        data_dict.pop('ratio_location')
        pr_list = []
        for key, val in data_dict.items():
            if val != '' and val != '0':
                partner = Partner.objects.get(key=key)
                try:
                    pr = PartnerRatio.objects.get(
                            partner=partner,
                            ratioset=ratio_set
                        )
                    pr.ratio=val
                    pr.save()
                    pr_list.append(pr)
                except PartnerRatio.DoesNotExist:
                    pr = PartnerRatio.objects.create(
                            partner=partner,
                            ratio=val,
                            ratioset=ratio_set
                        )
                    pr_list.append(pr)
        
        all = self.object.partnerratio_set.all()
        for qs in all:
            if qs not in pr_list:
                qs.delete()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(RatioSetUpdateView, self).get_context_data(**kwargs)
        partners_ratio = self.object.get_ratio_set()
        partners_keys = {}
        for ratios in partners_ratio:
            partners_keys[ratios.partner.key] = ratios.ratio
        context['partners_keys'] = partners_keys
        context['partners'] = Partner.objects.all()
        return context


class RatioSetDeleteView(LoginRequiredMixin, DeleteView):
    model = RatioSet
    success_url ="/ratio-sets/"


class BrandLocationRatioSetListView(LoginRequiredMixin, ListView):
    template_name = 'sts/brand_location_ratio_set_list.html'
    model = BrandLocationDefinedSetsRatio
    ordering = ['-created_at']
    paginate_by = 10
    utils = Utils()

    def get_queryset(self):
        qs = BrandLocationDefinedSetsRatio.objects.all().order_by('created_at')

        brand_id = self.request.GET.get('brand')
        if brand_id:
            qs = qs.filter(
                brand__id=brand_id
            )

        loc_id = self.request.GET.get('loc')
        if loc_id:
            qs = qs.filter(
                location__id=loc_id
            )

        sl_id = self.request.GET.get('sl')
        if sl_id:
            qs = qs.filter(
                search_location__id=sl_id
            )

        pg_id = self.request.GET.get('pg')
        if pg_id:
            qs = qs.filter(
                property_group__id=pg_id
            )

        return qs

    def paginate_queryset(self, queryset, page_size):
        paginate_by_url = self.request.GET.get("paginate_by")
        if paginate_by_url:
            self.request.session['paginate_by'] = paginate_by_url

        paginate_by_url = self.request.session.get('paginate_by', page_size)

        page_number = self.request.GET.get('page', '1')
        return self.utils.paginate_by_chunk_size_or_page_number(
            queryset, chunk_size=paginate_by_url, page_number=int(page_number)
        )

    def get_context_data(self, **kwargs):
        context = super(BrandLocationRatioSetListView, self).get_context_data(**kwargs)
        context['brands'] = Brand.objects.all()
        context['locations'] = Location.objects.all()
        context['search_locations'] = SearchLocation.objects.all()
        context['property_groups'] = PropertyGroup.objects.all()
        return context


class BrandLocationRatioSetCreateView(LoginRequiredMixin, CreateView):
    template_name = 'sts/brand_location_ratio_set_create.html'
    model = BrandLocationDefinedSetsRatio
    fields = ['brand', 'location', 'search_location', 'device', 'property_group', 'ratio_set']

    def form_valid(self, form):
        # latest_id = BrandLocationDefinedSetsRatio.objects.aggregate(Max('id'))['id__max']
        # form.instance.id = latest_id + 1
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class BrandLocationRatioSetUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'sts/brandlocationratioset_form.html'
    model = BrandLocationDefinedSetsRatio
    form_class = BrandLocationDefinedSetsRatioForm


class BrandLocationRatioSetDetailsView(LoginRequiredMixin, DetailView):
    template_name = 'sts/brand_location_ratio_set_details.html'
    model = BrandLocationDefinedSetsRatio


class BrandLocationRatioSetHistoryView(LoginRequiredMixin, DetailView):
    template_name = 'sts/brand_location_ratio_set_hitory_list.html'
    model = BrandLocationDefinedSetsRatio


class BrandLocationRatioSetDeleteView(LoginRequiredMixin, DeleteView):
    model = BrandLocationDefinedSetsRatio
    success_url = "/brand-location-ratio-sets/"


class CloneBrandLocationRatioSetView(LoginRequiredMixin, DetailView):
    template_name = 'sts/brand_location_ratio_set_clone_create.html'
    model = BrandLocationDefinedSetsRatio
    fields = ['brand', 'location', 'search_location', 'device', 'property_group', 'ratio_set']

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)

        brands = Brand.objects.all().exclude(id=self.object.brand.id)
        context['obj'] = self.object
        context['brands'] = brands
        return TemplateResponse(request, 'sts/brand_location_ratio_set_clone_create.html', context)
    
    def post(self, request, *args, **kwargs):
        object_id = request.POST.get('object_id')
        brand_ids = request.POST.getlist('brands')

        user_id = request.user.id

        arg_data = f"--user_id {user_id} --object_id {object_id} --brand_ids '{brand_ids}'"

        try:
            django_command = f'python manage.py clone_ratio_set {arg_data}'
            subprocess.Popen(
                django_command,
                shell=True,
                text=True,
            )
        except Exception as err:
            print(f'Sub process running err: {err}')

        messages.info(request, 'Cloning in progress...')

        return HttpResponseRedirect('/brand-location-ratio-sets/')


class BrandLocationRatioSetBulkCloneView(LoginRequiredMixin, TemplateView):
    template_name = 'sts/brand_location_ratio_set_bulk_clone.html'

    def get(self, request, *args, **kwargs):
        brands = Brand.objects.order_by('-name')
        ratio_sets = request.GET.get('brand_location_ratio_set_ids')
        if not ratio_sets:
            messages.info(request, f"Bulk clone selected items not found.")
            return redirect(reverse_lazy('sts:brand-location-ratio-set-list'))

        ratio_sets = [int(i) for i in ratio_sets.split(',')]
        selected_objects = []
        selected_objects.extend(BrandLocationDefinedSetsRatio.objects.filter(id__in=ratio_sets))

        context = {
            'brands': brands,
            'selected_objects': selected_objects
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        ratio_set_ids = request.POST.getlist('selected_objects')
        brand_ids = request.POST.getlist('brands')
        user_id = request.user.id

        arg_data = f"--user_id {user_id} --ratio_set_ids '{ratio_set_ids}' --brand_ids '{brand_ids}'"

        try:
            django_command = f'python manage.py bulk_clone_ratio_set {arg_data}'
            subprocess.Popen(
                django_command,
                shell=True,
                text=True,
            )
        except Exception as err:
            print(f'Sub process running err: {err}')
        messages.info(request, 'Bulk clone of ratio sets is in progress')
        return redirect(reverse_lazy('sts:brand-location-ratio-set-list'))


class BulkCreateBrandLocationRatioSetView(LoginRequiredMixin, TemplateView):
    template_name = 'sts/brand_location_ratio_set_bulk_create.html'

    def get(self, reqest, *args, **kwargs):
        form = BrandLocationDefinedSetsRatioBulkInsertForm
        partners = Partner.objects.all()
        locations = Location.objects.all()
        devices = Device.objects.all()
        search_locations = SearchLocation.objects.all()
        accommodation_types = PropertyGroup.objects.all()
        context = {
            'form': form,
            'partners': partners,
            'locations': locations,
            'devices': devices,
            'search_locations': search_locations,
            'accommodation_types': accommodation_types
        }
        return render(reqest, 'sts/brand_location_ratio_set_bulk_create.html', context)

    def post(self, request, *args, **kwargs):
        data = request.POST
        form = BrandLocationDefinedSetsRatioBulkInsertForm(data)
        if form.is_valid():
            loc_id = data.get('location')
            search_loc_id = data.get('search_location')
            property_group_id = data.get('property_group')
            device_ids = data.getlist('devices')

            ratio_set_title = data.get('ratio_set_title')
            partner_ratios = data.getlist('partner_ratios')
            partner_ids = data.getlist('partner_ids')

            ratio_set = RatioSet.objects.create(
                title=ratio_set_title
            )
            ratios = [(pid, v) for (pid, v) in zip(partner_ids, partner_ratios) if v != '']
            for pid, ratio in ratios:
                print(f"Partner id: {pid} and ratio {ratio}")
                partner = Partner.objects.get(id=int(pid))

                PartnerRatio.objects.create(
                    partner=partner,
                    ratio=int(ratio),
                    ratioset=ratio_set
                )
            ratio_set.save()

            brand_id_list = data.getlist('brands')
            if brand_id_list:
                user_id = request.user.id
                ratio_set_id = ratio_set.id

                data_str = (f"--user_id {user_id} --brand_id_list '{brand_id_list}' --device_ids '{device_ids}' "
                            f"--loc_id {loc_id} --search_loc_id {search_loc_id} "
                            f"--property_group_id {property_group_id} --ratio_set_id {ratio_set_id}")

                try:
                    django_command = f'python manage.py bulk_create_ratio_sets {data_str}'
                    subprocess.Popen(
                        django_command,
                        shell=True,
                        text=True,
                    )
                except Exception as err:
                    print(f'Sub process running err: {err}')
                messages.info(request, "Bulk create is in progress")
        return HttpResponseRedirect('/brand-location-ratio-sets/')


class BulkUpdateBrandLocationRatioSetView(LoginRequiredMixin, TemplateView):
    template_name = 'sts/brand_location_ratio_set_bulk_update.html'

    def get(self, request, *args, **kwargs):
        ratio_sets = request.GET.get('brand_location_ratio_set_ids')
        if not ratio_sets:
            messages.info(request, f"Select update items.")
            return redirect(reverse_lazy('sts:brand-location-ratio-set-list'))

        ratio_sets = [int(i) for i in ratio_sets.split(',')]
        selected_objects = []
        selected_objects.extend(BrandLocationDefinedSetsRatio.objects.filter(id__in=ratio_sets))

        form = BrandLocationDefinedSetsRatioBulkInsertForm
        partners = Partner.objects.all()
        locations = Location.objects.all()
        devices = Device.objects.all()
        search_locations = SearchLocation.objects.all()
        accommodation_types = PropertyGroup.objects.all()
        context = {
            'form': form,
            'selected_objects': selected_objects,
            'partners': partners,
            'locations': locations,
            'devices': devices,
            'search_locations': search_locations,
            'accommodation_types': accommodation_types
        }
        return TemplateResponse(request, 'sts/brand_location_ratio_set_bulk_update.html', context)
    
    def post(self, request, *args, **kwargs):
        ratio_set_title = request.POST.get('ratio_set_title')
        partner_ratios = request.POST.getlist('partner_ratios')
        partner_ids = request.POST.getlist('partner_ids')
        location = request.POST.get('location')
        device = request.POST.get('device')
        property_group = request.POST.get('property_group')
        search_location = request.POST.get('search_location')
        selected_object_ids = request.POST.getlist('selected_objects')

        selected_objects = BrandLocationDefinedSetsRatio.objects.filter(id__in=selected_object_ids)
        ratio_set = RatioSet.objects.create(
            title=ratio_set_title
        )
        ratios = [(pid, v) for (pid, v) in zip(partner_ids, partner_ratios) if v != '']
        for pid, ratio in ratios:
            print(f"Partner id: {pid} and ratio {ratio}")
            partner = Partner.objects.get(id=int(pid))

            PartnerRatio.objects.create(
                partner=partner,
                ratio=int(ratio),
                ratioset=ratio_set
            )

        if location:
            location = Location.objects.get(id=location)

        if device:
            device = Device.objects.get(id=device)

        if property_group:
            property_group = PropertyGroup.objects.get(id=property_group)

        if search_location:
            search_location = SearchLocation.objects.get(id=search_location)

        for obj in selected_objects:
            obj.ratio_set = ratio_set
            obj.location = location if location else obj.location
            obj.device = device if device else obj.device
            obj.property_group = property_group if property_group else obj.property_group
            obj.search_location = search_location if search_location else obj.search_location
            created_by = request.user
            change_reason = f"Ratio set Bulk update by {created_by} at {timezone.now()}"
            obj._change_reason = change_reason
            obj.created_by = created_by
            obj.save()

        messages.success(request, f"Bulk update performed on {len(selected_objects)} objects.")
        return HttpResponseRedirect('/brand-location-ratio-sets/')


class S3RatioSetJsonStatusView(LoginRequiredMixin, TemplateView):
    template_name = 'sts/s3_file_change_status_list.html'

    def get(self, request, *args, **kwargs):
        utils = Utils()
        core_service = CoreService()
        bucket_name = config('S3_BUCKET_NAME')
        s3_config = core_service.s3_config()
        # s3 connection
        s3_client = core_service.s3_connection(s3_config)
        brands = Brand.objects.all()
        site_env = config('SITE_ENV', 'dev')
        site_s3_ratio_status_list = []

        def process_brand_data(brand, s3_client, bucket_name, site_env, site_s3_ratio_status_list):
            site_key = brand.key.lower()
            s3_object_name = f"{site_env}/{site_key}.json"
            updated_at = 'No cache'
            last_updated = 0
            try:
                s3_response = s3_client.get_object(Bucket=bucket_name, Key=s3_object_name)
                s3_object_body = s3_response.get('Body')
                content_str = s3_object_body.read().decode()
                s3_file_json = json.loads(content_str)
                updated_at = s3_file_json.get('updated_at') if s3_file_json.get('updated_at') else 'No cache'
                if s3_file_json.get('updated_at'):
                    last_updated = utils.get_time_difference(s3_file_json.get('updated_at', ''),
                                                             datetime.datetime.now())
            except s3_client.exceptions.NoSuchBucket as e:
                print(e)
            except s3_client.exceptions.NoSuchKey as e:
                print(e)
            except Exception as err:
                print(f'S3 file getting error: {err}')

            site_s3_ratio_status_list.append({
                'name': brand.name,
                'site_key': site_key,
                'updated_at': updated_at,
                'last_updated': last_updated
            })

        with concurrent.futures.ThreadPoolExecutor() as executor:
            # Use partial to create a function with fixed arguments
            process_partial = partial(process_brand_data, s3_client=s3_client, bucket_name=bucket_name,
                                      site_env=site_env, site_s3_ratio_status_list=site_s3_ratio_status_list)

            # Submit tasks for each brand
            futures = [executor.submit(process_partial, brand) for brand in brands]
            # Wait for all tasks to complete
            concurrent.futures.wait(futures)
        site_s3_ratio_status_list = sorted(site_s3_ratio_status_list, key=lambda x: x['name'])
        context = {
            'site_s3_ratio_status_list': site_s3_ratio_status_list
        }
        return TemplateResponse(request, 'sts/s3_file_change_status_list.html', context)


class InvalidAndCache(LoginRequiredMixin, TemplateView):

    def get(self, request, *args, **kwargs):
        site_key = kwargs.get('site_key')
        site_key = site_key.strip()
        utils = Utils()
        ratio_service = STSAPIService()
        core_service = CoreService()
        s3_service = S3Services()
        bucket_name = config('S3_BUCKET_NAME')
        s3_config = core_service.s3_config()
        s3_client = core_service.s3_connection(s3_config)
        site_env = config('SITE_ENV', 'dev')
        try:
            data = ratio_service.get_ratio(site_key.upper())
            data['updated_at'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            site_key = site_key.lower()
            file_location = f"{BASE_STS_PATH}{site_key}.json"
            utils.remove_files(BASE_STS_PATH, f"{site_key}.json")
            utils.write_json_file(data=data, file_location=file_location)
            s3_object_name = f"{site_env}/{site_key}.json"
            s3_service.s3_file_process(bucket_name, file_location, s3_object_name, s3_client)
        except Exception as err:
            print(err)
        return redirect('/check-s3-ratio-set-status/')
