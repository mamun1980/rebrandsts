from django import forms
from apps.partners.models import Partner
from .models import Brand


class BrandForm(forms.ModelForm):
    partners = forms.ModelMultipleChoiceField(
        queryset=Partner.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'size': 10, 'class': 'form-check-input ps-2 d-inline-block'})
    )

    class Meta:
        model = Brand
        fields = ['name', 'alias', 'key', 'partners']
