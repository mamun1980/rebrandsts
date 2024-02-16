from rest_framework import serializers
from .models import PropertyGroup, PropertyType, PartnerPropertyMapping


class PropertyGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyGroup
        fields = ['id', 'name',  'create_date', 'update_date']

    def to_representation(self, instance):
        types = instance.propertytype_set.all()
        property_types = [str(v.name) for v in types]
        data = {
            instance.name: property_types
        }
        return data


class PartnerPropertyMappingSerializer(serializers.ModelSerializer):
    class Meta:
        model = PartnerPropertyMapping
        fields = '__all__'
