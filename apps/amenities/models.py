from django.db import models
from django.urls import reverse
from apps.partners.models import Partner


class PartnerAmenityType(models.Model):
    name = models.CharField(max_length=100, blank=False, null=False)
    partner = models.ForeignKey(Partner, blank=False, null=False, on_delete=models.CASCADE)
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    def get_absolute_url(self):
        return reverse('partner-amenity-type-detail', args=[str(self.id)])

    def __str__(self):
        return f"{self.partner.name}__{self.name}"


class AmenityTypeCategory(models.Model):
    name = models.CharField(max_length=100, blank=False, null=False)
    partner_amenity_type = models.ManyToManyField(PartnerAmenityType, blank=True)
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    def get_absolute_url(self):
        return reverse('amenity-type-detail', args=[str(self.id)])

    def get_partner_amenity_type(self):
        return ", ".join([pamenity.name for pamenity in self.partner_amenity_type.all()])

    class Meta:
        verbose_name = "LeftTravel Amenity Type"
        verbose_name_plural = "LeftTravel Amenity Types"

    def __str__(self):
        return self.name
