from django.db import models
from apps.brands.models import Brand
from apps.partners.models import Partner, Provider
from apps.property.models import PropertyGroup
from apps.sts.models import Location, Device


BRAND_TYPE = (('rentals', 'Rentals'), ('hotels', 'Hotels'))


# Create your models here.
class BrandLocationPartnerProperty(models.Model):
    # id = models.PositiveSmallIntegerField(unique=True, primary_key=True)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    partner = models.ForeignKey(Partner, on_delete=models.CASCADE)
    property_group = models.ForeignKey(PropertyGroup, on_delete=models.CASCADE)
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    providers = models.ManyToManyField(Provider, through='BrandLocationPartnerPropertyProvider')

    class Meta:
        unique_together = ['brand', 'location', 'partner', 'property_group', 'device']
        verbose_name = "(Kayak) Provider Order"  # Singular display name
        verbose_name_plural = "(Kayak) Provider Orders"

    def __str__(self):
        return f"{self.id}__{self.brand}__{self.location}__{self.partner}__{self.property_group}__{self.device}"


class BrandLocationPartnerPropertyProvider(models.Model):
    loc = models.ForeignKey(BrandLocationPartnerProperty, on_delete=models.CASCADE)
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE)
    order = models.PositiveSmallIntegerField(default=1)
    status = models.SmallIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['loc', 'provider']
        verbose_name = "Provider Order"  # Singular display name
        verbose_name_plural = "Provider Orders"


class SQSTerms(models.Model):
    # id = models.PositiveSmallIntegerField(unique=True, primary_key=True)
    keyword = models.CharField(max_length=50, blank=False, null=False, unique=True)
    brand_type = models.CharField(max_length=50, blank=False, null=False, choices=BRAND_TYPE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "SQS Term"  # Singular display name
        verbose_name_plural = "SQS Terms"

    def __str__(self):
        return f"{self.keyword}-{self.brand_type}"


class SetList(models.Model):
    # id = models.PositiveSmallIntegerField(unique=True, primary_key=True)
    name = models.CharField(max_length=50, blank=False, null=False)
    description = models.TextField(max_length=2500, blank=True, null=True)
    solr_fields = models.JSONField(blank=True, null=True)
    default = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class SiteEnableSets(models.Model):
    # id = models.PositiveSmallIntegerField(unique=True, primary_key=True)
    set_list = models.ForeignKey(SetList, blank=True, null=True, on_delete=models.CASCADE)
    site = models.ForeignKey(Brand, blank=True, null=True, on_delete=models.CASCADE)
    active = models.BooleanField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.id}"


class SetListES(models.Model):
    # id = models.PositiveSmallIntegerField(unique=True, primary_key=True)
    name = models.CharField(max_length=50, blank=False, null=False)
    description = models.TextField(max_length=2500, blank=True, null=True)
    es_fields = models.JSONField(blank=True, null=True)
    default = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    index_name = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        verbose_name = "Set List ES"  # Singular display name
        verbose_name_plural = "Set List ES"

    def __str__(self):
        return self.name


class SiteEnableSetsES(models.Model):
    # id = models.PositiveSmallIntegerField(unique=True, primary_key=True)
    set_list = models.ForeignKey(SetListES, blank=True, null=True, on_delete=models.CASCADE)
    brands = models.ManyToManyField(Brand)
    active = models.BooleanField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def show_brands(self):
        brands = self.brands.all()
        brand_list = [brand.name for brand in brands]
        return ", ".join(brand_list)

    class Meta:
        verbose_name = "Site Enable Set ES"  # Singular display name
        verbose_name_plural = "Site Enable Sets ES"

    def __str__(self):
        return f"{self.id}"
