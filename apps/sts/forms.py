from django import forms
from django.forms.models import BaseInlineFormSet
from core.utils import Utils
from .models import *


class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = ['location_type', 'country_code', 'country']


class SearchLocationForm(forms.ModelForm):

    class Meta:
        model = SearchLocation
        fields = ['search_location']

    class Media:
        js = (
            'admin/js/jquery.init.js',
            'js/location_search.js',
        )


class RatioSetForm(forms.ModelForm):
    class Meta:
        model = RatioSet
        fields = '__all__'
        exclude = ['ratio_title']


class RatioSetAdminForm(forms.ModelForm):
    class Meta:
        model = RatioSet
        fields = '__all__'
        exclude = ['ratio_location', 'ratio_title']


class PartnerRatioForm(forms.ModelForm):
    class Meta:
        model = PartnerRatio
        fields = '__all__'


class PartnerRatioBulkUpdateForm(forms.ModelForm):
    ratio = forms.IntegerField()

    class Meta:
        model = PartnerRatio
        exclude = ['ratioset']


class PartnerRatioInlineFormSet(BaseInlineFormSet):
    def clean(self):
        cleaned_data = super().clean()
        partners = []
        total_ratio = 0
        for frm in self.forms:
            is_deleted = frm.cleaned_data.get('DELETE')
            if not is_deleted and frm.cleaned_data.get('ratio') and frm.cleaned_data.get('partner'):
                total_ratio += frm.cleaned_data.get('ratio')
                partner = frm.cleaned_data.get('partner')
                if partner not in partners:
                    partners.append(partner)
                else:
                    raise forms.ValidationError(f"{partner.name} added twice")

        if total_ratio != 100:
            raise forms.ValidationError("Total ratio should be equal to 100")

        return cleaned_data


class DuplicatePropertyPartnerOrderForm(forms.ModelForm):
    class Meta:
        model = DuplicatePropertyPartnerOrder
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        feeds = Partner.objects.exclude(feed=12)
        vrbo = Partner.objects.get(key='VRBO')
        unique_feeds = [f.id for f in feeds]
        unique_feeds.append(vrbo.id)
        partners = Partner.objects.filter(id__in=unique_feeds)

        self.fields['partner'].queryset = partners


# class DuplicatePropertyPartnerOrderInlineFormSet(BaseInlineFormSet):
#     def clean(self):
#         cleaned_data = super().clean()
#         partners = []
#         total_ratio = 0
#         for frm in self.forms:
#             is_deleted = frm.cleaned_data.get('DELETE')
#             if not is_deleted and frm.cleaned_data.get('ratio') and frm.cleaned_data.get('partner'):
#                 total_ratio += frm.cleaned_data.get('ratio')
#                 partner = frm.cleaned_data.get('partner')
#                 if partner not in partners:
#                     partners.append(partner)
#                 else:
#                     raise forms.ValidationError(f"{partner.name} added twice")
#
#         if total_ratio != 100:
#             raise forms.ValidationError("Total ratio should be equal to 100")
#
#         return cleaned_data


class BrandLocationDefinedSetsRatioForm(forms.ModelForm):
    change_reason = forms.CharField(required=False, widget=forms.Textarea)

    class Meta:
        model = BrandLocationDefinedSetsRatio
        fields = ['brand', 'location', 'search_location', 'device', 'property_group', 'ratio_set', 'created_by',
                  'change_reason']

    def save(self, commit=True):
        instance = super(BrandLocationDefinedSetsRatioForm, self).save(commit=False)
        change_reason = self.cleaned_data['change_reason']
        instance._change_reason = change_reason

        if commit:
            instance.save()

        site_key_list = [instance.brand.key]
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

        return instance


class BrandLocationDefinedSetsRatioBulkInsertForm(forms.ModelForm):
    brands = forms.ModelMultipleChoiceField(
        widget=forms.CheckboxSelectMultiple(attrs={'size': 10, 'class': 'form-check-input ps-2 d-inline-block'}),
        queryset=Brand.objects.all()
    )
    devices = forms.ModelMultipleChoiceField(
        widget=forms.CheckboxSelectMultiple(attrs={'size': 10, 'class': 'form-check-input ps-2 d-inline-block'}),
        queryset=Device.objects.all(),
        required=True
    )
    property_group = forms.ModelChoiceField(
        widget=forms.Select,
        queryset=PropertyGroup.objects.all(),
        required=True
    )

    class Meta:
        model = BrandLocationDefinedSetsRatio
        fields = ['location', 'search_location', 'property_group', 'ratio_set']
    
    def clean_devices(self):
        devices = self.cleaned_data.get('devices')
        if not devices:
            raise forms.ValidationError("You must select at least one device.")
        return devices


class CustomWidget(forms.widgets.Select):
    template_name = 'admin/sts/widgets/select.html'

    def render(self, name, value, attrs=None, renderer=None):
        context = self.get_context(name, value, attrs)
        return self._render(self.template_name, context, renderer)


class LeaveBehindPopUnderRulesForm(forms.ModelForm):
    property_type = forms.ChoiceField(
        choices=(('rental', 'Rental'), ('hotel', 'Hotel')),
    )
    # partner = forms.ModelChoiceField(
    #     queryset=Utils.get_filtered_by_12_partners()
    # )
    # tiles_lb_partner = forms.ModelChoiceField(
    #     queryset=Utils.get_filtered_by_12_partners()
    # )
    # details_lb_partner = forms.ModelChoiceField(
    #     queryset=Utils.get_filtered_by_12_partners()
    # )
    # popunder_partner = forms.ModelChoiceField(
    #     queryset=Utils.get_filtered_by_12_partners()
    # )

    class Meta:
        model = LeaveBehindPopUnderRules
        fields = '__all__'


