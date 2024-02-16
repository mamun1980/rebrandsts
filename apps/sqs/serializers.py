from rest_framework import serializers
import json
from .models import SQSTerms, SetList, SiteEnableSets, SetListES, SiteEnableSetsES


class SQSTermsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SQSTerms
        fields = ['id', 'keyword', 'brand_type']


class SetWithRatioSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteEnableSets
        fields = '__all__'


class SetListESSerializer(serializers.ModelSerializer):
    class Meta:
        model = SetListES
        fields = '__all__'


class DefaultSetListESSerializer(serializers.ModelSerializer):
    class Meta:
        model = SetListES
        fields = '__all__'


class ESFieldsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteEnableSetsES
        fields = '__all__'
    
    def to_representation(self, instance):
        es_fields = instance.set_list.es_fields
        es_fields_json = json.loads(es_fields)
        es_fields_json['id'] = instance.set_list.id
        return es_fields_json


class DefaultQueryESSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteEnableSetsES
        fields = '__all__'

    def to_representation(self, instance):
        es_fields = instance.set_list.es_fields
        es_fields_json = json.loads(es_fields)
        data = {}
        data['name'] = instance.set_list.name
        data["es_fields"] = es_fields_json
        data['default'] = 1
        return data


class SiteEnableSetsESSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteEnableSetsES
        fields = '__all__'

    def to_representation(self, instance):
        es_fields = instance.set_list.es_fields
        es_fields_json = json.loads(es_fields)
        data = {}
        data[instance.set_list.name] = es_fields_json

        return data
