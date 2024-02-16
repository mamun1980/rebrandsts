from django.db import models
from django.urls import reverse
from apps.brands.models import Brand
from apps.partners.models import Partner


BRAND_TYPE = (('rentals', 'Rentals'), ('hotels', 'Hotels'))


class PropertyGroup(models.Model):
    # id = models.PositiveSmallIntegerField(unique=True, primary_key=True)
    name = models.CharField(max_length=100, blank=False, null=False)
    property_ordering = models.PositiveSmallIntegerField(default=0)
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    @property
    def property_type_sets(self):
        pts = self.propertytype_set.all()
        names = [pt.name for pt in pts]
        return names


class PropertyCategory(models.Model):
    # id = models.PositiveSmallIntegerField(unique=True, primary_key=True)
    name = models.CharField(max_length=100, blank=False, null=False)
    group = models.ForeignKey(PropertyGroup, blank=True, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class PropertyType(models.Model):
    # id = models.PositiveSmallIntegerField(unique=True, primary_key=True)
    name = models.CharField(max_length=100, blank=False, null=False)
    brand = models.ForeignKey(Brand, blank=True, null=True, on_delete=models.CASCADE)
    brand_type = models.CharField(max_length=50, blank=True, null=True, choices=BRAND_TYPE)
    accommodation_type = models.ManyToManyField(PropertyGroup)
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    def get_absolute_url(self):
        return reverse('property-types-detail', args=[str(self.id)])

    class Meta:
        verbose_name = "LeftTravel Type"
        verbose_name_plural = "LeftTravel Types"

    def __str__(self):
        return self.name


# class PropertyGroupOfTypes(models.Model):
#     property_type = models.ForeignKey(PropertyType, on_delete=models.CASCADE)
#     property_group = models.ForeignKey(PropertyGroup, on_delete=models.CASCADE)


class PartnerPropertyType(models.Model):
    # id = models.IntegerField(unique=True, primary_key=True)
    name = models.CharField(max_length=100, blank=False, null=False)
    partner = models.ForeignKey(Partner, blank=False, null=False, on_delete=models.CASCADE)
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    def get_absolute_url(self):
        return reverse('partner-property-types-detail', args=[str(self.id)])

    def __str__(self):
        return f"{self.partner.name}__{self.name}"


class PartnerPropertyMapping(models.Model):
    property_type = models.ForeignKey(PropertyType, on_delete=models.CASCADE)
    partner_property = models.ForeignKey(PartnerPropertyType, on_delete=models.CASCADE)

    def get_absolute_url(self):
        return reverse('property-mapping-detail', args=[str(self.pk)])

    def __str__(self):
        return f"{self.partner_property.name}->{self.property_type.name}"
