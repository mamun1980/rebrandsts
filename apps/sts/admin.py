from datetime import datetime, date, timedelta
from django.utils import timezone
import concurrent.futures
import math
import boto3

from django.contrib import admin, messages
from django.test import RequestFactory
from django.core.cache import cache
from django.shortcuts import render, redirect
from apps.sts.filters import MultiSelectDropdownFilter
from admin_extra_buttons.api import ExtraButtonsMixin, button
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.conf import settings
from pathlib import Path
from django.utils.html import format_html
from django.http import HttpResponseRedirect
from django.db.models import Avg, Count, Min, Sum
from simple_history.admin import SimpleHistoryAdmin
from core.settings.base import BASE_DIR
from apps.analytics.models import VrsAnalytics
# from api.tasks import generate_ratio_api_response_task
from .models import *
from .forms import (RatioSetAdminForm, PartnerRatioForm, PartnerRatioInlineFormSet, BrandLocationDefinedSetsRatioForm,
                     BrandLocationDefinedSetsRatioBulkInsertForm, DuplicatePropertyPartnerOrderForm,
                    SearchLocationForm, LeaveBehindPopUnderRulesForm)
from .views import confirm_bulk_update, perform_bulk_update, invalidate_cache_and_recache
from decouple import config
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from functools import partial
from core.utils import Utils
from core.service import CoreService
from api.services import STSAPIService
from apps.sts.service.s3_service import S3Services
from api import BASE_STS_PATH
from apps.sts.serializers import LeaveBehindPopUnderRulesSerializer


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ['id', 'type', 'sort_order', 'created_at', 'updated_at']
    ordering = ['sort_order']
    readonly_fields = ['id']

    def save_model(self, request, obj, form, change):
        obj.created_by = request.user
        # if not obj.id:
        #     latest_id = Device.objects.aggregate(Max('id'))['id__max']
        #     obj.id = latest_id + 1 if latest_id else 1
        super().save_model(request, obj, form, change)


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ['id', 'country_code', 'country', 'location_type']
    list_filter = ['location_type']
    search_fields = ['country_code']
    ordering = ['id']
    readonly_fields = ['id']
    view_on_site = False

    def save_model(self, request, obj, form, change):
        obj.created_by = request.user
        # if not obj.id:
        #     latest_id = Location.objects.aggregate(Max('id'))['id__max']
        #     obj.id = latest_id + 1 if latest_id else 1
        super().save_model(request, obj, form, change)


@admin.register(LocationType)
class LocationTypeAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(SearchLocation)
class SearchLocationAdmin(admin.ModelAdmin):
    add_form_template = 'admin/sts/search_location/change_form.html'
    form = SearchLocationForm
    list_display = ['id', 'place_id', 'search_location', 'sort_order', 'location_type', 'location_level', 'type_level', 'slug',
                    'ep_location_id', 'update_date']
    list_filter = ['location_type']
    search_fields = ['search_location']
    ordering = ['-update_date']
    readonly_fields = ['id']

    def changeform_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['google_map_api_key'] = config('GOOGLE_MAP_API_KEY')

        response = super().changeform_view(
            request, object_id, form_url=form_url, extra_context=extra_context,
        )
        return response


class PartnerRatioInline(admin.TabularInline):
    model = PartnerRatio
    form = PartnerRatioForm
    formset = PartnerRatioInlineFormSet
    extra = 0


class DuplicatePropertyPartnerOrderInline(admin.TabularInline):
    model = DuplicatePropertyPartnerOrder
    form = DuplicatePropertyPartnerOrderForm
    # formset = PartnerRatioInlineFormSet
    extra = 0


class LeaveBehindPopUnderRulesInline(admin.StackedInline):
    model = LeaveBehindPopUnderRules
    # formset = PartnerRatioInlineFormSet
    extra = 0


class RatioSetInline(admin.TabularInline):
    model = RatioSet
    extra = 0


class BrandLocationDefinedSetsRatioInline(admin.StackedInline):
    model = BrandLocationDefinedSetsRatio
    extra = 0


# @admin.register(PartnerRatio)
# class PartnerRatioAdmin(admin.ModelAdmin):
#     list_display = ['partner', 'ratio']


@admin.register(RatioLocation)
class RatioLocationAdmin(admin.ModelAdmin):
    list_display = ['id', 'location_name']
    ordering = ['id']
    readonly_fields = ['id']

    def save_model(self, request, obj, form, change):
        obj.created_by = request.user
        # if not obj.id:
        #     latest_id = RatioLocation.objects.aggregate(Max('id'))['id__max']
        #     obj.id = latest_id + 1 if latest_id else 1
        super().save_model(request, obj, form, change)


@admin.register(RatioSet)
class RatioSetAdmin(admin.ModelAdmin):
    inlines = [PartnerRatioInline]
    form = RatioSetAdminForm
    add_form = RatioSetAdminForm
    list_display = ['id', 'title', 'ratio_title']
    ordering = ['-updated_at', '-id']
    readonly_fields = ['ratio_title']
    view_on_site = False

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('ratio-title-update/<int:object_id>/', self.admin_site.admin_view(self.ratio_title_change), name='ratio_title_update'),
        ]
        return custom_urls + urls

    def ratio_title_change(self, request, object_id):
        try:
            ratio_set = RatioSet.objects.get(id=object_id)
            brand_locations = ratio_set.brandlocationdefinedsetsratio_set.all()
            titles = [b.save() for b in brand_locations]
            ret = super().response_change(request, object_id)
            return ret
        except Exception as e:
            messages.error(request, e)

    def save_related(self, request, form, formsets, change):
        super(RatioSetAdmin, self).save_related(request, form, formsets, change)
        form.instance.save()


@admin.register(BrandLocationDefinedSetsRatio)
class BrandLocationDefinedSetsRatioAdmin(ExtraButtonsMixin, SimpleHistoryAdmin):
    # is_nav_sidebar_enabled = False
    inlines = [DuplicatePropertyPartnerOrderInline]
    change_list_template = "admin/sts/brandlocationdefinedsetsratio_list.html"
    form = BrandLocationDefinedSetsRatioForm
    list_display = ['clone', 'id', 'brand_name', 'location_name', 'search_location_name', 'device_name',
                    'property_group_name', 'ratio_set_title', 'prediction']
    list_filter = [
        ('ratio_set', MultiSelectDropdownFilter),
        ('brand', MultiSelectDropdownFilter),
        ('location', MultiSelectDropdownFilter),
        ('search_location', MultiSelectDropdownFilter),
        ('property_group', MultiSelectDropdownFilter),
        ('device', MultiSelectDropdownFilter),

    ]
    # search_fields = ['brand__name', 'location__country', 'ratio_set__ratio_title']
    readonly_fields = ['created_by']
    list_display_links = ['id']
    ordering = ['-updated_at']
    actions = ['bulk_update', 'bulk_clone_ratio_sets', 'bulk_update_partner_orders']
    view_on_site = False
    history_list_display = ["ratio", "created_by"]

    class Media:
        js = ('js/jquery.min.js', 'js/jquery.multiselect.js')
        css = {
             'all': ('css/jquery.multiselect.css', 'css/custom_style.css',)
        }

    def save_model(self, request, obj, form, change):
        obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('clone/<int:object_id>/', self.admin_site.admin_view(self.clone_ratio_set), name='clone_ratio_set'),
            path('bulk-create/', self.admin_site.admin_view(self.bulk_create_view), name='bulk_create'),
            path('bulk-update-partner-orders/', self.admin_site.admin_view(self.bulk_update_partner_orders),
                 name='bulk-update-partner-orders'),
            path('perform-bulk-update-partner-orders/', self.admin_site.admin_view(
                self.perform_bulk_update_partner_orders), name='perform-bulk-update-partner-orders'),
            path('bulk-clone-ratio-set/', self.admin_site.admin_view(self.bulk_clone_ratio_set_view),
                 name='bulk_clone_ratio_set'),
            path('confirm-bulk-update/', self.admin_site.admin_view(self.confirm_bulk_update),
                 name='confirm-bulk-update'),
            path('perform-bulk-update/', perform_bulk_update, name='perform-custom-action'),
            path('prediction-board/<int:object_id>/', self.admin_site.admin_view(self.prediction_board),
                 name='prediction-board'),
            path('check-s3-ratio-set-status/', self.admin_site.admin_view(S3RatioSetJsonStatusAdminView.as_view()),
                 name='check-s3-ratio-set-status'),
            path('invalid-and-cache-again/<str:site_key>/', self.admin_site.admin_view(invalidate_cache_and_recache),
                 name='invalid-and-cache-again'),
        ]
        return custom_urls + urls

    def confirm_bulk_update(self, request):
        selected_object_ids = request.session.pop('selected_object_ids', [])
        if not selected_object_ids:
            return HttpResponseRedirect('/sts/brandlocationdefinedsetsratio/')
        selected_objects = BrandLocationDefinedSetsRatio.objects.filter(id__in=selected_object_ids)
        partners = Partner.objects.all()
        devices = Device.objects.all()
        locations = Location.objects.all()
        accommodation_types = PropertyGroup.objects.all()
        search_locations = SearchLocation.objects.all()
        context = dict(
            self.admin_site.each_context(request)
        )
        context['selected_objects'] = selected_object_ids
        context['partners'] = partners
        context['devices'] = devices
        context['accommodation_types'] = accommodation_types
        context['locations'] = locations
        context['search_locations'] = search_locations
        
        return render(request, 'admin/sts/confirm_bulk_update.html', context)

    def ratio(self, obj):
        title = ', '.join([ratio.replace('_', ' ') for ratio in obj.ratio_set_title.split(' ')])
        return title

    def get_list_per_page(self, request):
        page_size = request.GET.get('list_per_page', self.list_per_page)
        request.session['list_per_page'] = page_size
        return page_size

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        list_per_page = self.get_list_per_page(request)

        if list_per_page == 'all':
            self.list_per_page = 10000
        elif list_per_page == 'default':
            self.list_per_page = 10
        else:
            self.list_per_page = int(list_per_page)

        extra_context['page_size'] = self.list_per_page

        return super().changelist_view(request, extra_context)

    @admin.action
    def bulk_update(self, request, queryset):
        request.session['selected_object_ids'] = [obj.id for obj in queryset]
        return HttpResponseRedirect('/sts/brandlocationdefinedsetsratio/confirm-bulk-update/')

    @admin.action
    def bulk_clone_ratio_sets(self, request, queryset):
        selected_object_ids = [obj.id for obj in queryset]
        brands = Brand.objects.all()
        request.session['selected_object_ids'] = selected_object_ids
        context = dict(
            self.admin_site.each_context(request)
        )
        context['selected_object_ids'] = selected_object_ids
        context['brands'] = brands
        context['total_counts'] = queryset.count()

        return render(request, 'admin/sts/bulk_clone_ratio_sets.html', context)

    @admin.action
    def bulk_update_partner_orders(self, request, queryset):
        selected_object_ids = [obj.id for obj in queryset]
        # partners = Partner.objects.all()
        feeds = Partner.objects.exclude(feed=12)
        vrbo = Partner.objects.get(key='VRBO')
        unique_feeds = [f.id for f in feeds]
        unique_feeds.append(vrbo.id)
        partners = Partner.objects.filter(id__in=unique_feeds)

        request.session['selected_object_ids'] = selected_object_ids
        context = dict(
            self.admin_site.each_context(request)
        )
        context['selected_object_ids'] = selected_object_ids
        context['partners'] = partners
        context['total_counts'] = queryset.count()

        return render(request, 'admin/sts/bulk_update_partner_orders.html', context)

    def perform_bulk_update_partner_orders(self, request):
        data = request.POST
        ratio_set_ids = data.getlist('ratio_set_ids')
        partner_orders = data.getlist('partner_orders')
        partner_ids = data.getlist('partner_ids')
        orders = [(pid, v) for (pid, v) in zip(partner_ids, partner_orders) if v != '']

        arg_data = f"--orders '{orders}' --ratiosetids '{ratio_set_ids}'"

        try:
            django_command = f"python manage.py bulk_update_partner_orders {arg_data}"
            subprocess.Popen(
                django_command,
                shell=True,
                text=True,
            )
        except Exception as err:
            print(f'Sub process running err: {err}')

        return HttpResponseRedirect('/sts/brandlocationdefinedsetsratio/')

    def ratio_set_short(self, obj):
        ratiosets = obj.ratio_set.partnerratio_set.all()
        title = ''
        for rs in ratiosets:
            title += f"{rs.partner.key}{rs.ratio}%"
        return title

    def clone(self, obj):
        return format_html(
        '<a class="button" href="{}">Clone</a>&nbsp;',
            reverse('admin:clone_ratio_set', args=[obj.pk]),
        )
    clone.short_description = 'Actions'
    clone.allow_tags = True

    def prediction(self, obj):
        if obj.predicted_ratio_title:
            rev_url = reverse("admin:prediction-board", args=[obj.pk])
            url = f"<a class='button' href='{rev_url}'>{obj.predicted_ratio_title}</a>"
            return format_html(url)
        else:
            return None

    prediction.short_description = 'Prediction Title'
    prediction.allow_tags = True

    @button(html_attrs={'style': 'background-color:#DC6C6C;color:black'})
    def bulk_create_new_ratio_set(self, request):
        return HttpResponseRedirect('/sts/brandlocationdefinedsetsratio/bulk-create/')

    @button(html_attrs={'style': 'background-color:#DC6C6C;color:black'})
    def download_prediction_data(self, request):
        
        s3_file = 'prediction_data/sts_prediction_data.json'
        local_file = Path(BASE_DIR / 'data/prediction_data/sts_prediction_data.json')
        if not local_file.exists():
            ValidationError('Prediction file does not exist. Please download first.')
            messages.error(request, "Prediction file does not exist. Please download first.")

        bucket_name = config('S3_BUCKET_NAME', '')
        aws_access_key_id = config('S3_ACCESS_KEY', '')
        aws_secret_access_key = config('S3_SECRET_ACCESS_KEY', '')
        s3_region = config('S3_REGION_NAME', '')

        if aws_access_key_id and aws_secret_access_key:
            s3_client = boto3.client('s3', aws_access_key_id=aws_access_key_id,
                                     aws_secret_access_key=aws_secret_access_key)
        else:
            s3_client = boto3.client('s3')

        try:
            s3_client.download_file(bucket_name, s3_file, local_file)

        except Exception as err:
            print(f'Error downloading prediction data: {err}')
            messages.warning(request, f"Error downloading prediction data: {err}")
        else:
            messages.info(request, "Download is done")

    @button(html_attrs={'style': 'background-color:#1995dc;color:black'})
    def update_predicted_ratio(self, request):
        local_file_path = 'data/prediction_data/sts_prediction_data.json'
        file_path = Path(local_file_path)
        if not file_path.is_file():
            ValidationError('Prediction file does not exist. Please download first.')
            messages.error(request, "Prediction file does not exist. Please download first.")
        else:
            # update_task = update_predicted_ratio_field_in_sts_db(file)
            try:
                django_command = f'python manage.py update_predicted_ratio_field_in_sts_db --file {local_file_path}'
                subprocess.Popen(
                    django_command,
                    shell=True,
                    text=True,
                )
            except Exception as err:
                print(f'Sub process running err: {err}')

            messages.info(request, "Update is in progress")

    @button(html_attrs={'style': 'background-color:#72B511;color:black'})
    def generate_and_upload_ratio_files_in_s3(self, request):
        brands = Brand.objects.all()
        site_key_list = [b.key for b in brands]
        print(f"{'*' * 50}")
        try:
            django_command = (f'python manage.py generate_ratio_set_json_and_upload_s3 --site_keys'
                              f' {",".join(site_key_list)}')
            subprocess.Popen(
                django_command,
                shell=True,
                text=True,
            )
        except Exception as err:
            print(f'Sub process running err: {err}')
        messages.info(request, "Generating and uploading ratio files for all sites in S3....")

    @button(html_attrs={'style': 'background-color:#FFA000;color:black'})
    def clear_cache(self, request):
        cache.clear()
        messages.info(request, "Cache cleared..")

    def clone_ratio_set(self, request, object_id):
        if request.method == 'POST':
            object_id = request.POST.get('object_id')
            brand_ids = request.POST.getlist('brands')
            user_id = request.user.id

            # clone_ratio_set_task.delay(user_id, object_id, brand_ids)
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

            return HttpResponseRedirect('/sts/brandlocationdefinedsetsratio/')
        else:
            bldsr = BrandLocationDefinedSetsRatio.objects.get(id=object_id)
            brands = Brand.objects.all().exclude(id=bldsr.brand.id)

            context = dict(
                self.admin_site.each_context(request),
            )
            context['brands'] = brands
            context['obj'] = bldsr
            return TemplateResponse(request, 'admin/sts/clone_ratio_page.html', context)

    def bulk_create_view(self, request):
        partners = Partner.objects.all()
        if request.method == 'POST':
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

                    # bulk_create_ratio_sets.delay(user_id, brand_id_list, device_ids, loc_id, search_loc_id,
                    #                              property_group_id, ratio_set_id)

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
            else:

                form_errors = form.errors
                context = dict(
                    self.admin_site.each_context(request)
                )

                context['form'] = form
                context['partners'] = partners
                context['form_errors'] = form_errors
                return TemplateResponse(request, 'admin/sts/bulk_create.html', context)

            return HttpResponseRedirect('/sts/brandlocationdefinedsetsratio/')
        else:
            form = BrandLocationDefinedSetsRatioBulkInsertForm
            context = dict(
                self.admin_site.each_context(request)
            )
            context['form'] = form
            context['partners'] = partners

        return TemplateResponse(request, 'admin/sts/bulk_create.html', context)

    def prediction_board(self, request, object_id):
        if request.method == 'GET':
            context = dict(
                self.admin_site.each_context(request)
            )
            try:
                # 
                brand_location_ratio_set = BrandLocationDefinedSetsRatio.objects.get(id=object_id)
                site_key = brand_location_ratio_set.brand.key
                site_name = brand_location_ratio_set.brand.name
                country_code = brand_location_ratio_set.location.country_code
                location_type = brand_location_ratio_set.location.location_type
                country_name = brand_location_ratio_set.location.country
                device = brand_location_ratio_set.device.type

                continent_list_file = Path(settings.BASE_DIR) / 'data/static_data/continent_list.json'
                if country_code == 'EU':
                    with open(continent_list_file, 'r') as fp:
                        continent_list_data = json.loads(fp.read())
                        country_code_list = continent_list_data.get('EU')
                elif country_code == 'NA' and location_type == 'continent':
                    with open(continent_list_file, 'r') as fp:
                        continent_list_data = json.loads(fp.read())
                        country_code_list = continent_list_data.get('NA')
                else:
                    country_code_list = [country_code]

                today = date.today()
                day = int(request.GET.get('d', '15'))
                report_date = today - timedelta(days=day)

                analytics = VrsAnalytics.objects.filter(device=device.lower(), site_key=site_key,
                                                        country_code__in=country_code_list,
                                                        transaction_date__gt=report_date)
                values = analytics.values('feed').annotate(total_count=Count('id'),
                                                           total_revenue=Sum('predicted_revenue'))
                partner_conversions = analytics.values('transaction_date__date', 'feed').annotate(
                    total_count=Count('id'), total_revenue=Sum('predicted_revenue')).order_by('-transaction_date__date')

                value_dict = {data['feed']: {'conversion': data['total_count'], 'revenue': data['total_revenue']} for
                              data in values}
                partner = {'VRBO': 12, 'BC': 11, 'AB': 16, 'HG': 22, 'TA': 19, 'KY': 23, 'TC': 20, 'EP': 24, 'LT': 25,
                           'HP': 26}
                feed = {v: k for k, v in partner.items()}
                # 
                ratio_title = brand_location_ratio_set.ratio_set_title
                prev_ratios = {pair.split('_')[0]: int(pair.split('_')[1][:-1]) for pair in ratio_title.split()}
                total_conversion = sum(entry['conversion'] for entry in value_dict.values())
                total_revenue = sum(entry['revenue'] for entry in value_dict.values())

                predicted_ratio_title = brand_location_ratio_set.predicted_ratio_title
                if predicted_ratio_title:
                    predicted_ratios = {p: int(r[:-1]) for ratio in predicted_ratio_title.split()
                                                 if int(ratio.split('_')[1][:-1]) > 0 for p, r in [ratio.split('_')]}

                else:
                    predicted_ratios = {p: int(r[:-1]) for ratio in ratio_title.split()
                                                 if int(ratio.split('_')[1][:-1]) > 0 for p, r in [ratio.split('_')]}

                conversion_details = []
                for partner_conversion in partner_conversions:
                    partner_key = feed[partner_conversion.get('feed')]
                    predicted_conversion = math.ceil(((
                                        partner_conversion.get('total_count')/prev_ratios.get(partner_key)) *
                                        predicted_ratios.get(partner_key)) if prev_ratios.get(partner_key) else (
                                        partner_conversion.get('total_count') * 1.2))
                    predicted_revenue = ((partner_conversion.get('total_revenue')/prev_ratios.get(partner_key)) *
                                         predicted_ratios.get(partner_key)) if prev_ratios.get(partner_key) else (
                                        partner_conversion.get('total_revenue') * 1.2)

                    # if partner_conversion.get('total_count') != 0:
                    #     conversion_increment = ((predicted_conversion - partner_conversion.get('total_count')) /
                    #                             partner_conversion.get('total_count')) * 100
                    # else:
                    #     conversion_increment = 'N/A'
                    #
                    # if partner_conversion.get('total_revenue') != 0:
                    #     revenue_increment = ((predicted_revenue - partner_conversion.get('total_revenue')) /
                    #                          partner_conversion.get('total_revenue')) * 100
                    # else:
                    #     revenue_increment = 'N/A'

                    conversion = {
                        "date": partner_conversion.get('transaction_date__date'),
                        "partner": partner_key,
                        "ratio": prev_ratios.get(partner_key),
                        "predicted_ratio": predicted_ratios.get(partner_key),
                        "conversion": partner_conversion.get('total_count'),
                        "predicted_conversion": predicted_conversion,
                        # "conversion_increment": conversion_increment,
                        "revenue": partner_conversion.get('total_revenue'),
                        "predicted_revenue": predicted_revenue,
                        # "revenue_increment": revenue_increment
                    }
                    conversion_details.append(conversion)

                total_predicted_conversion = 0
                total_predicted_revenue = 0
                for key, ratio in predicted_ratios.items():
                    if key in prev_ratios and partner.get(key) in value_dict:
                        prev_ratio = prev_ratios.get(key)
                        total_predicted_conversion += value_dict[partner[key]]['conversion'] * (ratio / prev_ratio)
                        total_predicted_revenue += value_dict[partner[key]]['revenue'] * (ratio / prev_ratio)
                    else:
                        total_predicted_conversion += total_conversion * (ratio/100) * 1.20
                        total_predicted_revenue += total_revenue * (ratio/100) * 1.20

                # 
                context['ratio_title'] = ratio_title
                context['predicted_ratio_title'] = predicted_ratio_title
                context['total_predicted_conversion'] = f"{total_predicted_conversion:.2f}"
                context['total_predicted_revenue'] = f"{total_predicted_revenue:.2f}" if total_predicted_revenue else None
                context['revenue'] = total_revenue
                context['conversion'] = math.ceil(total_conversion)
                context['today'] = today
                context['report_date'] = report_date
                context['conversion_details'] = conversion_details
                
                if total_predicted_conversion and total_conversion:
                    context['conversion_increment'] = ((total_predicted_conversion - total_conversion) / total_conversion) * 100
                else:
                    context['conversion_increment'] = -1

                if total_predicted_revenue and total_revenue:
                    context['revenue_increment'] = ((total_predicted_revenue - total_revenue) / total_revenue) * 100
                else:
                    context['revenue_increment'] = -1

                context['site_key'] = site_key
                context['site_name'] = site_name
                context['country_code'] = country_code
                context['country_name'] = country_name
                context['device'] = device

                chart_data = {}
                predicted_chart_data = {}

                partner_ratio = {partner_key: prev_ratios.get(partner_key, 0) for partner_key in partner.keys()}
                predicted_ratio = {partner_key: predicted_ratios.get(partner_key, 0) for partner_key in partner.keys()}
                for data in conversion_details:
                    if data['date'].isoformat() not in chart_data:
                        chart_data[data['date'].isoformat()] = partner_ratio
                        predicted_chart_data[data['date'].isoformat()] = predicted_ratio
                    else:
                        chart_data[data['date'].isoformat()].update(partner_ratio)
                        predicted_chart_data[data['date'].isoformat()].update(predicted_ratio)

                context['chart_labels'] = ','.join([f"'{data}'" for data in chart_data.keys()])
                datasets = {}
                predicted_datasets = {}
                for k, value in chart_data.items():
                    for key in partner.keys():
                        if key not in datasets:
                            datasets[key] = [value.get(key) if value.get(key) else 0]
                        else:
                            datasets[key].append(
                                value.get(key) if value.get(key) else 0
                            )

                for k, value in predicted_chart_data.items():
                    for key in partner.keys():
                        if key not in predicted_datasets:
                            predicted_datasets[key] = [value.get(key) if value.get(key) else 0]
                        else:
                            predicted_datasets[key].append(
                                value.get(key) if value.get(key) else 0
                            )

                context['datasets'] = datasets
                context['predicted_datasets'] = predicted_datasets

            except Exception as e:
                pass
            return TemplateResponse(request, 'admin/sts/prediction_board.html', context)

    @staticmethod
    def process_brand_location(brand, bl_ratio_set, request):
        try:
            bl_rs = BrandLocationDefinedSetsRatio.objects.get(
                brand=brand,
                location=bl_ratio_set.location,
                search_location=bl_ratio_set.search_location,
                device=bl_ratio_set.device,
                property_group=bl_ratio_set.property_group
            )
            bl_rs.ratio_set = bl_ratio_set.ratio_set
            bl_rs.ratio_set_title = bl_rs.ratio_set_short_title
            bl_rs.updated_at = timezone.now()
            return bl_rs
        except BrandLocationDefinedSetsRatio.DoesNotExist:
            return BrandLocationDefinedSetsRatio(
                brand=brand,
                location=bl_ratio_set.location,
                search_location=bl_ratio_set.search_location,
                device=bl_ratio_set.device,
                property_group=bl_ratio_set.property_group,
                ratio_set=bl_ratio_set.ratio_set,
                ratio_set_title=bl_ratio_set.ratio_set_short_title,
                
                brand_name=brand.name,
                property_group_name=bl_ratio_set.property_group.name,
                location_name=f"{bl_ratio_set.location.country} ({bl_ratio_set.location.country_code})",
                search_location_name=bl_ratio_set.search_location.search_location,
                device_name=bl_ratio_set.device.type,
                
                created_by=request.user,
                created_at=timezone.now(),
                updated_at=timezone.now()
            )
    
    def process_brand_locations(self, brand, ratio_set_list, request):
        new_ratio_sets = []
        update_ratio_sets = []
        tuple_dict = {}

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = []
            for bl_ratio_set in ratio_set_list:
                ratio_tuple = (brand.id, bl_ratio_set.location.id, bl_ratio_set.search_location.id,
                               bl_ratio_set.device.id, bl_ratio_set.property_group.id)
                if ratio_tuple not in tuple_dict:
                    tuple_dict[ratio_tuple] = 1
                    futures.append(executor.submit(self.process_brand_location, brand, bl_ratio_set, request))

            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if isinstance(result, BrandLocationDefinedSetsRatio):
                    update_ratio_sets.append(result)
                else:
                    new_ratio_sets.append(result)

        BrandLocationDefinedSetsRatio.objects.bulk_create(new_ratio_sets)
        BrandLocationDefinedSetsRatio.objects.bulk_update(update_ratio_sets, ['ratio_set', 'ratio_set_title', 'updated_at'])

    def bulk_clone_ratio_set_view(self, request):
        if request.method == 'POST':
            # import pdb; pdb.set_trace()
            ratio_set_ids = request.POST.getlist('ratio_set_ids')
            brand_ids = request.POST.getlist('brands')
            user_id = request.user.id
            # bulk_clone_ratio_set_task.delay(user_id, brand_ids, ratio_set_ids)
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

        return HttpResponseRedirect('/sts/brandlocationdefinedsetsratio/')
    

@admin.register(PredictedRatio)
class PredictedRatioAdmin(admin.ModelAdmin):
    list_display = ['user_id', 'predicted_ratio', 'predicted_ratio_title', 'prediction_date', 'revision']


class S3RatioSetJsonStatusAdminView(LoginRequiredMixin, TemplateView):
    template_name = 'admin/s3_file_change_status.html'
    debug = config('DEBUG')
    site_env = config('SITE_ENV')

    def get(self, request, *args, **kwargs):
        site_env = config('SITE_ENV')
        utils = Utils()
        bucket_name = config('S3_BUCKET_NAME')

        # s3 connection
        if config('DEBUG') and site_env == 'dev':
            s3_client = boto3.client(
                's3',
                aws_access_key_id=config("S3_ACCESS_KEY"),
                aws_secret_access_key=config("S3_SECRET_ACCESS_KEY"),
                region_name=config("S3_REGION_NAME")
            )

        else:
            s3_client = boto3.client('s3', region_name=config("S3_REGION_NAME"))

        try:
            response = s3_client.list_objects_v2(Bucket=bucket_name)
            keys = response.get('Contents')
        except Exception as e:
            print(e)
            keys = []

        brands = Brand.objects.all()
        site_s3_ratio_status_list = []
        site_data = {}
        for k in keys:
            key = k.pop('Key') if k.get('Key') else None
            if key and key.split("/")[0] == site_env:
                site_data[key] = k

        def process_brand_data(brand, file_meta):
            updated_at = 'No cache'
            last_updated = ''
            try:
                updated_at = file_meta.get('LastModified') if file_meta.get('LastModified') else 'No cache'
                if file_meta.get('LastModified'):
                    current_datetime = datetime.now(timezone.utc)
                    td = current_datetime - updated_at
                    # last_updated = f"{td.days} days {td.seconds} minutes ago"
                    hours, minutes, seconds = utils.seconds_to_days_hours_minutes(td.seconds)
                    last_updated += f"{hours} hours " if hours > 0 else ''
                    last_updated += f"{minutes} minutes " if minutes > 0 else ''
                    last_updated += f"{seconds} seconds " if seconds > 0 else ''
                    last_updated += " ago!"

            except Exception as err:
                print(f'S3 file getting error: {err}')

            site_s3_ratio_status_list.append({
                'name': brand.name,
                'site_key': site_key,
                'updated_at': updated_at,
                'last_updated': last_updated
            })

        for brand in brands:
            site_key = brand.key.lower()
            s3_object_name = f"{site_env}/{site_key}.json"
            if s3_object_name in site_data.keys():
                file_meta = site_data.get(s3_object_name)
                process_brand_data(brand, file_meta)

        site_s3_ratio_status_list = sorted(site_s3_ratio_status_list, key=lambda x: x['name'])
        context = dict(
            admin.site.each_context(self.request)
        )
        context['site_s3_ratio_status_list'] = site_s3_ratio_status_list
        return TemplateResponse(request, 'admin/s3_file_change_status.html', context)


class InvalidAndCache(LoginRequiredMixin, TemplateView):

    def post(self, request, url):
        data = {"status": "Success"}
        return data

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
            data['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            site_key = site_key.lower()
            file_location = f"{BASE_STS_PATH}{site_key}.json"
            utils.remove_files(BASE_STS_PATH, f"{site_key}.json")
            utils.write_json_file(data=data, file_location=file_location)
            s3_object_name = f"{site_env}/{site_key}.json"
            s3_service.s3_file_process(bucket_name, file_location, s3_object_name, s3_client)
        except Exception as err:
            print(err)
        return redirect(reverse('admin:check-s3-ratio-set-status'))


@admin.register(LeaveBehindPopUnderRules)
class LeaveBehindPopUnderRulesAdmin(ExtraButtonsMixin, admin.ModelAdmin):
    # form = LeaveBehindPopUnderRulesForm
    change_list_template = 'admin/sts/leavebehindpopunderrules/change_list.html'
    list_display = ['partner', 'location', 'device', 'property_types', 'tiles_leave_behind_partner',
                    'details_leave_behind_partner', 'pop_under_partner']
    list_filter = ['partner', 'location', 'device', 'property_type']

    def property_types(self, obj):
        return obj.property_type
    property_types.short_description = 'Property Types'

    def tiles_leave_behind_partner(self, obj):
        return obj.tiles_lb_partner
    tiles_leave_behind_partner.short_description = 'Tiles Leave Behind Partner'

    def details_leave_behind_partner(self, obj):
        return obj.details_lb_partner
    details_leave_behind_partner.short_description = 'Details Leave Behind Partner'

    def pop_under_partner(self, obj):
        return obj.popunder_partner
    pop_under_partner.short_description = 'Pop Under Partner'

    def get_urls(self):
        urls = super().get_urls()
        new_urls = [
            path('save-redirection-rules', self.admin_site.admin_view(self.save_redirection_rules),
                 name='save-redirection-rules')
        ]
        return urls + new_urls

    # def formfield_for_dbfield(self, db_field, **kwargs):
    #     formfield = super().formfield_for_dbfield(db_field, **kwargs)
    #
    #     if db_field.name == 'property_type':
    #         # Add a custom link to the right side of the field
    #         formfield.widget.attrs['class'] = 'custom-link-class'
    #         formfield.widget.attrs['data-href'] = '/sts/'
    #         formfield.widget.attrs['data-target'] = '_blank'  # Optional: open link in a new tab
    #
    #     return formfield

    def save_redirection_rules(self, request):
        rules = LeaveBehindPopUnderRules.objects.all()
        if not rules:
            messages.warning(request, 'No records for leave behind & pop under redirection found...!')
            return redirect("/sts/leavebehindpopunderrules/")
        serializer = LeaveBehindPopUnderRulesSerializer(rules, many=True)
        data = serializer.data
        result_object = {k: v for item in data for k, v in item.items()}

        s3_region_name = config.config.get("S3_REGION_NAME")
        bucket_name = config.config.get('S3_BUCKET_NAME')
        env = config.config.get('SITE_ENV')
        if env == 'dev':
            s3 = boto3.client(
                's3',
                aws_access_key_id=config.config.get("S3_ACCESS_KEY"),
                aws_secret_access_key=config.config.get("S3_SECRET_ACCESS_KEY"),
                region_name=s3_region_name
            )
        else:
            s3 = boto3.client('s3', region_name=s3_region_name)

        file_path = "redirection-rules.json"
        with open(f"data/{file_path}", 'w') as fd:
            json_data = json.dumps(result_object)
            fd.write(json_data)
        s3.upload_file(f"data/{file_path}", bucket_name, f"{env}/{file_path}")

        return redirect("/sts/leavebehindpopunderrules/")


@admin.register(DuplicatePropertyPartnerOrder)
class DuplicatePropertyPartnerOrder(admin.ModelAdmin):
    list_display = ['id', 'bldsr', 'partner', 'order']
    list_filter = ['bldsr']