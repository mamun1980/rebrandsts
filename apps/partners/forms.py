from django import forms
from .models import Partner, Provider


class PartnerForm(forms.ModelForm):
    
    class Meta:
        model = Partner
        fields = ['name','key', 'domain_name', 'feed', 'sort_order']


class ProviderForm(forms.ModelForm):
    class Meta:
        model = Provider
        fields = ['name', 'provider_id']
