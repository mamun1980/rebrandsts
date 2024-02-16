from rest_framework import serializers
from .models import Partner, PartnerProvider


class PartnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Partner
        fields = '__all__'


class PartnerProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = PartnerProvider
        fields = '__all__'

    def to_representation(self, instance):
        return instance.provider.provider_id
