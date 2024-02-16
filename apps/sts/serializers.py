from rest_framework import serializers
from .models import BrandLocationDefinedSetsRatio, RatioGroup, Location, RatioSet, LeaveBehindPopUnderRules

RENTAL_TYPES = ("Villa", "Cabin", "Apartment", "House", "Cottage", "Bed & Breakfast")


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['country_code', 'country', 'location_type']


class RatioSetSerializer(serializers.ModelSerializer):
    class Meta:
        model = RatioSet
        fields = ['id', 'title', 'ratio_location', 'created_at', 'updated_at']


class RatioGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = RatioGroup
        fields = '__all__'

    def to_representation(self, instance):
        partners_ratio = instance.ratio_set.partnerratio_set.all()
        data = {p.partner.id:p.ratio for p in partners_ratio if p.ratio}
        return data


class LeaveBehindPopUnderRulesSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveBehindPopUnderRules
        fields = '__all__'

    def to_representation(self, instance):
        title = (f"{instance.partner.feed}-{instance.location.country_code}-{instance.device.type.lower()}-"
                 f"{instance.property_type}")
        data = {}
        data[title] = {
            "tiles-lb": str(instance.tiles_lb_partner.feed),
            "details-lb": str(instance.details_lb_partner.feed),
            "details-pu": str(instance.popunder_partner.feed) if instance.popunder_partner else ""
        }
        return data