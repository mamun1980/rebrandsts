import subprocess

from django.db import models
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import Max
from django.utils.text import slugify
from django.contrib.auth.models import User
from simple_history.models import HistoricalRecords

from apps.partners.models import Partner
from apps.property.models import PropertyGroup, PropertyType
from apps.brands.models import Brand
import json
import requests
from decouple import config


class Device(models.Model):
    # id = models.PositiveSmallIntegerField(unique=True, primary_key=True)
    type = models.CharField(max_length=100, blank=False, null=False, unique=True)
    sort_order = models.SmallIntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.type


class Location(models.Model):
    # id = models.PositiveSmallIntegerField(unique=True, primary_key=True)
    location_type = models.CharField(max_length=50, blank=True, null=True,
                                     choices=(('continent', 'Continent'), ('country', 'Country')))
    country_code = models.CharField(max_length=100, blank=False, null=False)
    country = models.CharField(max_length=100, blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_absolute_url(self):
        return reverse('sts:locations-detail', args=[str(self.id)])

    def __str__(self):
        return f"{self.country} ({self.country_code})"


class LocationType(models.Model):
    name = models.CharField(max_length=100, blank=False, null=False, primary_key=True)

    def __str__(self):
        return self.name


class SearchLocation(models.Model):
    # id = models.PositiveSmallIntegerField(unique=True, primary_key=True)
    search_location = models.CharField(max_length=100, blank=False, null=False)
    place_id = models.CharField(max_length=100, blank=True, null=True)
    sort_order = models.SmallIntegerField(blank=True, null=True)
    ep_location_id = models.CharField(max_length=50, blank=False, null=False, unique=True)
    type_level = models.SmallIntegerField(blank=True, null=True)
    location_type = models.ForeignKey(LocationType, blank=True, null=True, on_delete=models.CASCADE)
    slug = models.CharField(max_length=100, blank=True, null=True)
    location_level = models.CharField(max_length=100, blank=True, null=True)
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.search_location}"
    
    def get_absolute_url(self):
        return reverse('sts:search-locations-list')

    def clean(self):
        token = config('TOKEN', '')
        corn_api_base_url = config('COMMON_CORN_API_BASE_URL', '')
        location_api_base_url = config('LOCATION_API_BASE_URL', '')

        if not token:
            raise ValidationError('Please set valid TOKEN in your .env file.')
        if not corn_api_base_url:
            raise ValidationError('Please set COMMON_CORN_API_BASE_URL in your .env file.')
        if not location_api_base_url:
            raise ValidationError('Please set LOCATION_API_BASE_URL in your .env file.')

        # if not self.id:
        #     latest_id = SearchLocation.objects.aggregate(Max('id'))['id__max']
        #     self.id = latest_id + 1 if latest_id else 1
        if not self.sort_order:
            sort_order = SearchLocation.objects.aggregate(Max('sort_order'))['sort_order__max']
            self.sort_order = sort_order + 1 if sort_order else 1

        search_location = self.search_location        
        location_api_url = f"{location_api_base_url}/v1/location?keyword={search_location}"
        location_api_response = requests.get(location_api_url)

        if location_api_response.status_code != 200:
            raise ValidationError(location_api_response.reason)

        location_data = location_api_response.json()
        location_id = location_data['GeoInfo']['LocationID']
        if not location_id:
            raise ValidationError("There is no location id for your search!")
        
        loc_exist = SearchLocation.objects.filter(ep_location_id=location_id).exists()
        if loc_exist:
            raise ValidationError("Location already exist!")
        
        corn_api_url = f"{corn_api_base_url}/api/v1/location-info/{location_id}/?format=json&token={token}"
        common__corn_api_response = requests.get(corn_api_url)

        if common__corn_api_response.status_code == 200:
            common_corn_data = common__corn_api_response.json()['data']
            location_type = common_corn_data.get('location_type')
            location_type_obj, created = LocationType.objects.get_or_create(name=location_type)
            location_level = common_corn_data.get('location_level')
            type_level = common_corn_data.get('type_level')
            google_place_id = common_corn_data.get('google_place_id')

            self.place_id = google_place_id
            self.ep_location_id = location_id
            self.location_level = location_level
            self.location_type = location_type_obj
            self.type_level = type_level
            self.slug = slugify(self.search_location)
                        
        else:
            raise ValidationError(common__corn_api_response.reason)
        

class RatioLocation(models.Model):
    # id = models.PositiveSmallIntegerField(unique=True, primary_key=True)
    location_name = models.CharField(max_length=100, blank=False, null=False)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.location_name}"


class RatioSet(models.Model):
    title = models.CharField(max_length=500, blank=True, null=True)
    ratio_title = models.CharField(max_length=500, blank=True, null=True)
    ratio_location = models.ForeignKey(RatioLocation, blank=True, null=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_absolute_url(self):
        return reverse('sts:ratio-set-detail', args=[str(self.id)])

    def save(self, *args, **kwargs):
        if self.pk:
            partners_ratio = self.partnerratio_set.all()
            key_list = []
            for pr in partners_ratio:
                if pr.ratio != 0:
                    key_val = f"{pr.partner.key}_{pr.ratio}%"
                    key_list.append(key_val)
            short_name = ' '.join(key_list)
            self.ratio_title = f"{self.pk}_{short_name}"
        return super(RatioSet, self).save(*args, **kwargs)

    def get_ratio_set(self):
        partners_ratio = self.partnerratio_set.all()
        return partners_ratio

    @property
    def ratio_location_name(self):
        if self.ratio_location:
            return self.ratio_location.location_name
        else:
            return 'Not set'

    def __str__(self):
        if self.title:
            title = self.title
        elif self.ratio_title:
            title = self.ratio_title
        else:
            title = 'Not set'
        return f"{title}"


class PartnerRatio(models.Model):
    partner = models.ForeignKey(Partner, on_delete=models.CASCADE)
    ratio = models.PositiveSmallIntegerField(validators=[MaxValueValidator(100), MinValueValidator(0)])
    ratioset = models.ForeignKey(RatioSet, blank=False, null=False, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['partner', 'ratioset']

    def __str__(self):
        return f"{self.partner.name} ({self.ratio})"


class RatioGroup(models.Model):
    # id = models.PositiveSmallIntegerField(unique=True, primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    ratio_set = models.ForeignKey(RatioSet, blank=True, null=True, on_delete=models.CASCADE)
    short_name = models.CharField(max_length=500, blank=True, null=True, editable=False)
    archived = models.BooleanField(default=0)
    click_weight_ratio = models.TextField(blank=True, null=True)
    click_ratio_tiles_plan = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.id}"

    def get_json_data(self):
        data = {
            "id": self.id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "ratio_set": self.ratio_set,
            "short_name": self.short_name,
            "archived": self.archived,
            "click_weight_ratio": self.click_weight_ratio,
            "click_ratio_tiles_plan": self.click_ratio_tiles_plan
        }
        return json.dumps(data)


class PredictedRatio(models.Model):
    user_id = models.CharField(max_length=50)
    # brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    # location = models.ForeignKey(Location, on_delete=models.CASCADE)
    # device = models.ForeignKey(Device, on_delete=models.CASCADE)

    # ratio = models.JSONField(blank=True, null=True)
    # conversion = models.PositiveIntegerField(default=0)
    # revenue = models.DecimalField(decimal_places=2, max_digits=10, default=0.0)

    predicted_ratio = models.JSONField(blank=True, null=True)
    predicted_ratio_title = models.CharField(max_length=100, blank=True, null=True, editable=False)

    # predicted_conversion = models.PositiveIntegerField(default=0)
    # predicted_revenue = models.DecimalField(decimal_places=2, max_digits=10, default=0.0)

    prediction_date = models.DateField(blank=False, null=False)
    revision = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user_id', 'prediction_date']

    def __str__(self) -> str:
        return f"{self.user_id}"


class BrandLocationDefinedSetsRatio(models.Model):
    # id = models.PositiveSmallIntegerField(unique=True, primary_key=True)
    brand_location_id = models.PositiveSmallIntegerField(blank=True, null=True)
    defined_set_name = models.CharField(max_length=500, blank=True, null=True)
    ratio_group = models.ForeignKey(RatioGroup, blank=True, null=True, on_delete=models.CASCADE)
    ratio_group_data = models.JSONField(blank=True, null=True, editable=False)
    ratio_set = models.ForeignKey(RatioSet, blank=True, null=True, on_delete=models.CASCADE)
    ratio_set_data = models.JSONField(blank=True, null=True, editable=False)
    ratio_set_title = models.CharField(max_length=100, null=True, blank=True, editable=False)
    predicted_ratio = models.ForeignKey(PredictedRatio, null=True, blank=True, on_delete=models.CASCADE)
    predicted_ratio_title = models.CharField(max_length=100, blank=True, null=True, editable=False)
    property_group = models.ForeignKey(PropertyGroup, blank=True, null=True, on_delete=models.CASCADE)
    property_group_name = models.CharField(max_length=100, null=True, blank=True, editable=False)
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    device_name = models.CharField(max_length=100, null=True, blank=True, editable=False)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    location_name = models.CharField(max_length=100, null=True, blank=True, editable=False)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    brand_name = models.CharField(max_length=100, null=True, blank=True, editable=False)
    search_location = models.ForeignKey(SearchLocation, on_delete=models.CASCADE)
    search_location_name = models.CharField(max_length=100, null=True, blank=True, editable=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.PositiveSmallIntegerField(default=1)
    date = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords(history_change_reason_field=models.TextField(null=True))

    def get_absolute_url(self):
        return reverse('sts:brand-location-ratio-set-detail', args=[str(self.id)])

    class Meta:
        unique_together = ['brand', 'location', 'search_location', 'device', 'property_group']
        verbose_name = "Brand Location Ratio Set"  # Singular display name
        verbose_name_plural = "Brand Location Ratio Sets"

    def __str__(self):
        return f"{self.id}"
    
    def save(self, *args, **kwargs):
        self.ratio_set_title = self.ratio_set.ratio_title
        self.brand_name = self.brand.name
        self.property_group_name = self.property_group.name if self.property_group else ''
        self.location_name = f"{self.location.country} ({self.location.country_code})"
        self.search_location_name = self.search_location.search_location if self.search_location else ''
        self.device_name = self.device.type
        self.predicted_ratio_title = self.predicted_ratio.predicted_ratio_title if self.predicted_ratio else ''
        super(BrandLocationDefinedSetsRatio, self).save(*args, **kwargs)

    @property
    def ratio_set_short_title(self):
        ratiosets = self.ratio_set.partnerratio_set.all()
        key_list = []
        for pr in ratiosets:
            if pr.ratio != 0:
                key_val = f"{pr.partner.key}_{pr.ratio}%"
                key_list.append(key_val)
        title = ' '.join(key_list)
        return title
    

class DuplicatePropertyPartnerOrder(models.Model):
    bldsr = models.ForeignKey(BrandLocationDefinedSetsRatio, blank=False, null=False, on_delete=models.CASCADE)
    partner = models.ForeignKey(Partner, on_delete=models.CASCADE)
    order = models.PositiveSmallIntegerField(validators=[MaxValueValidator(100), MinValueValidator(0)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['bldsr', 'partner']

    def __str__(self):
        return f"{self.partner.name} ({self.order})"


class LeaveBehindPopUnderRules(models.Model):
    partner = models.ForeignKey(Partner, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    # property_type = models.ForeignKey(PropertyType, on_delete=models.CASCADE)
    property_type = models.CharField(max_length=50, choices=(('rental', 'Rental'), ('hotel', 'Hotel')))

    tiles_lb_partner = models.ForeignKey(Partner, blank=True, null=True, on_delete=models.SET_NULL,
                                         related_name='tiles_lb_partner', verbose_name="Tiles Leave Behind Partner")
    details_lb_partner = models.ForeignKey(Partner, blank=True, null=True, on_delete=models.SET_NULL,
                                        related_name='details_lb_partner', verbose_name="Details Leave Behind Partner")
    popunder_partner = models.ForeignKey(Partner, blank=True, null=True, on_delete=models.SET_NULL,
                                         related_name='popunder_partner', verbose_name="Pop Under Partner",)

    class Meta:
        # unique_together = ['partner', 'location', 'device', 'property_type']
        verbose_name = "Leave Behind & PopUnder Rule"
        verbose_name_plural = "Leave Behind & PopUnder Rules"

