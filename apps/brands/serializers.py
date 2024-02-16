from rest_framework import serializers
from .models import Brand, StaticSiteMapUrl, DynamicSiteMapUrl


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = '__all__'


class StaticSiteMapUrlSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaticSiteMapUrl
        fields = '__all__'


class DynamicSiteMapUrlSerializer(serializers.ModelSerializer):
    class Meta:
        model = DynamicSiteMapUrl
        fields = '__all__'
