from collections.abc import Iterable
from django.urls import reverse
from django.db import models
from django.contrib.postgres.fields import ArrayField
from apps.partners.models import Partner, Provider


class Brand(models.Model):
    # id = models.PositiveSmallIntegerField(unique=True, primary_key=True)
    name = models.CharField(max_length=100, blank=False, null=False, unique=True)
    alias = models.CharField(max_length=100, blank=True, null=True)
    key = models.CharField(max_length=10, blank=True, null=True)
    date = models.DateTimeField(blank=True, null=True)
    sort_order = models.PositiveSmallIntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    partners = models.ManyToManyField(Partner, through='BrandsPartners')

    def get_absolute_url(self):
        return reverse('brand-detail', args=[str(self.id)])

    def __str__(self):
        return f"{self.name}"

    def get_partners(self):
        return self.brandspartners_set.all()


class BrandsPartners(models.Model):
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    partner = models.ForeignKey(Partner, on_delete=models.CASCADE)
    # brand_partner_priority = models.PositiveSmallIntegerField(default=0)


class BrandsProviders(models.Model):
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE)
    # brand_partner_priority = models.PositiveSmallIntegerField(default=0)


class StaticSiteMapUrl(models.Model):
    id = models.PositiveSmallIntegerField(unique=True, primary_key=True)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    static_sitemap = ArrayField(models.CharField(max_length=100, blank=True, null=True))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class DynamicSiteMapUrl(models.Model):
    id = models.PositiveSmallIntegerField(unique=True, primary_key=True)
    category_listing_url = models.CharField(max_length=300, blank=True, null=True)
    mapping_category_listing = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
