from rest_framework import serializers
from apps.amenities.models import PartnerAmenityType, AmenityTypeCategory


class AmenityTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AmenityTypeCategory
        fields = ['id', 'name', 'partner_amenity_type', 'create_date', 'update_date']


class AmenityTypeUpdateDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = AmenityTypeCategory
        fields = ['id', 'name', 'partner_amenity_type', 'create_date', 'update_date']
        read_only_field = ['id']


class PartnerAmenityTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PartnerAmenityType
        fields = ['id', 'name', 'partner', 'create_date', 'update_date']


class PartnerAmenityTypeUpdateDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = PartnerAmenityType
        fields = ['id', 'name', 'partner', 'create_date', 'update_date']
        read_only_field = ['id']

