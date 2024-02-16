from django.db import models
from django.urls import reverse


# Create your models here.
class Partner(models.Model):
    # id = models.PositiveSmallIntegerField(unique=True, primary_key=True)
    name = models.CharField(max_length=100, blank=False, null=False)
    key = models.CharField(max_length=10, blank=True, null=True, unique=True)
    domain_name = models.CharField(max_length=100, blank=True, null=True, unique=True)
    date = models.DateTimeField(blank=True, null=True)
    feed = models.PositiveSmallIntegerField(blank=True, null=True)
    sort_order = models.SmallIntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_absolute_url(self):
        return reverse('partners-detail', args=[str(self.id)])

    def __str__(self):
        return f"{self.name}"


class Provider(models.Model):
    provider_id = models.CharField(max_length=50, blank=False, null=False, unique=True)
    name = models.CharField(max_length=100, blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}"


class PartnerProvider(models.Model):
    partner = models.ForeignKey(Partner, on_delete=models.CASCADE)
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE)
    order = models.PositiveSmallIntegerField(default=0)
    date = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Partner Provider(Kayak)"  # Singular display name
        verbose_name_plural = "Partner Providers(Kayak)"  # Plural display name


