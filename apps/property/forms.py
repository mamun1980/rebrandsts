from django import forms
from .models import PartnerPropertyMapping, PartnerPropertyType, PropertyType, PropertyGroup


class PartnerPropertyMappingForm(forms.ModelForm):
    def __init__(self, *args,**kwargs):
        super (PartnerPropertyMappingForm, self ).__init__(*args,**kwargs)
        ppm_all = PartnerPropertyMapping.objects.values_list('partner_property', flat=True).distinct()
        self.fields['partner_property'].queryset = PartnerPropertyType.objects.all().exclude(id__in=ppm_all)

    class Meta:
        model = PartnerPropertyMapping
        fields = ['partner_property']


class PropertyTypeForm(forms.ModelForm):
    accommodation_type = forms.ModelMultipleChoiceField(
        queryset=PropertyGroup.objects.all(),
        widget=forms.SelectMultiple(attrs={'size': 10}),
        required=False
    )

    class Meta:
        model = PropertyType
        fields = ['name', 'brand', 'brand_type', 'accommodation_type']


class PartnerPropertyTypeForm(forms.ModelForm):
    class Meta:
        model = PartnerPropertyType
        fields = ['name', 'partner']
