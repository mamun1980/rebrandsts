from django import forms
from django_json_widget.widgets import JSONEditorWidget
from django.forms.widgets import TextInput, Textarea
import json
from apps.brands.models import Brand
from .models import SetListES, SiteEnableSetsES


class JsonViewWidget(Textarea):

    def format_value(self, value):
        if value:
            value = json.loads(value)
        else:
            value = {}
        return value


class SetListESForm(forms.ModelForm):

    class Meta:
        model = SetListES
        fields = "__all__"
        widgets = {
            'es_fields': JSONEditorWidget()
        }


class SetListESNewForm(forms.ModelForm):
    # es_fields = forms.CharField(widget=JsonViewWidget)

    class Meta:
        model = SetListES
        fields = "__all__"

    def clean_es_fields(self):
        # Validate and handle JSON data as needed
        json_data = self.cleaned_data['es_fields']
        try:
            json.loads(json_data)
        except json.JSONDecodeError:
            raise forms.ValidationError("Invalid JSON data")
        return json_data

    class Meta:
        model = SetListES
        fields = ["name", "description", "es_fields"]


class SiteEnableSetsESForm(forms.ModelForm):
    brands = forms.ModelMultipleChoiceField(
        queryset=Brand.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'size': 10, 'class': 'form-check-input ps-2 d-inline-block', 'name': 'brands'})
    )
    active = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'size': 10, 'class': 'form-check-input ps-2 d-inline-block'})
    )

    class Meta:
        model = SiteEnableSetsES
        fields = ['set_list', 'brands', 'active']
