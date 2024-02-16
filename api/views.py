from rest_framework import viewsets, mixins, status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Max
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.decorators import authentication_classes
from django.views.decorators.vary import vary_on_cookie, vary_on_headers
from apps.brands.models import Brand, StaticSiteMapUrl, DynamicSiteMapUrl
from apps.brands.serializers import StaticSiteMapUrlSerializer, DynamicSiteMapUrlSerializer
from apps.sqs.models import SQSTerms, BrandLocationPartnerProperty, BrandLocationPartnerPropertyProvider, \
    SetList, SiteEnableSets, SetListES, SiteEnableSetsES
from apps.sqs.serializers import (SQSTermsSerializer, SetWithRatioSerializer, DefaultQueryESSerializer,
                                  SetListESSerializer, SiteEnableSetsESSerializer, ESFieldsSerializer, DefaultSetListESSerializer)
from apps.property.models import PropertyGroup, PartnerPropertyMapping, PartnerPropertyType
from apps.property.serializers import PropertyGroupSerializer, PartnerPropertyMappingSerializer
from apps.sts.models import BrandLocationDefinedSetsRatio, RatioGroup, Location, RatioSet, LeaveBehindPopUnderRules
from apps.sts.serializers import (RatioSetSerializer, RatioGroupSerializer, LocationSerializer,
                                  LeaveBehindPopUnderRulesSerializer)
from apps.partners.serializers import PartnerProviderSerializer, PartnerSerializer
from apps.partners.models import PartnerProvider, Partner
from collections import defaultdict
import concurrent.futures
import time, json
from .services import STSAPIService
from apps.amenities.models import PartnerAmenityType, AmenityTypeCategory
from apps.amenities.serializers import (
    AmenityTypeSerializer, AmenityTypeUpdateDeleteSerializer, PartnerAmenityTypeUpdateDeleteSerializer,
    PartnerAmenityTypeSerializer
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


class PartnerAPIView(viewsets.ReadOnlyModelViewSet):
    queryset = Partner.objects.all()
    serializer_class = PartnerSerializer


class StaticSiteMapUrlAPIView(viewsets.ReadOnlyModelViewSet):
    queryset = StaticSiteMapUrl.objects.all()
    serializer_class = StaticSiteMapUrlSerializer


class DynamicSiteMapUrlAPIView(viewsets.ReadOnlyModelViewSet):
    queryset = DynamicSiteMapUrl.objects.all()
    serializer_class = DynamicSiteMapUrlSerializer


class RatioSetViewSet(viewsets.ModelViewSet):
    queryset = RatioSet.objects.all()
    serializer_class = RatioSetSerializer


class LocationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Location.objects.all()
    # serializer_class = LocationSerializer

    def list(self, request):
        brand_key = request.query_params.get('site')
        if brand_key:
            try:
                brand = Brand.objects.get(key=brand_key.upper())
                blds = BrandLocationDefinedSetsRatio.objects.filter(brand=brand).values('location')
                locations = Location.objects.filter(id__in=blds)
                country = []
                continent = []
                for loc in locations:
                    if loc.location_type == 'country':
                        country.append(loc.country_code)
                    else:
                        continent.append(loc.country_code)
                data = {
                    "continent": continent,
                    "country": country
                }
            except Brand.DoesNotExist as e:
                data = {
                    "error": f"you site {brand_key} does not exist!"
                }
            return Response(data)

        locations = Location.objects.all()
        serializer = LocationSerializer(locations, many=True)
        return Response(serializer.data)


class SQSTermViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SQSTerms.objects.all()
    serializer_class = SQSTermsSerializer

    def list(self, request, *args, **kwargs):
        qs = SQSTerms.objects.all()
        ha_terms = []
        bc_terms = []
        for term in qs:
            if term.brand_type == 'rentals':
                ha_terms.append(term.keyword)
            else:
                bc_terms.append(term.keyword)

        data = {
            "ha_terms": ha_terms,
            "bc_terms": bc_terms
        }
        return Response(data=data, status=200)


class PropertyTypeRefressAPIView(viewsets.GenericViewSet, mixins.CreateModelMixin,):
    queryset = PartnerPropertyType.objects.all()
    serializer_class = PartnerPropertyMappingSerializer

    def create(self, request):
        post_data = request.data
        new_prop = {}
        for feed, props in post_data.items():
            partner = Partner.objects.filter(feed=feed)[0]
            for prop in props:
                is_exists = PartnerPropertyType.objects.filter(name=prop, partner=partner).exists()
                if not is_exists:
                    PartnerPropertyType.objects.create(name=prop, partner=partner)
                    if feed in new_prop.keys():
                        new_prop[feed].append(prop)
                    else:
                        new_prop[feed] = [prop]
        data = {
            "status": "Success",
            "result": new_prop
        }
        return Response(data, status=status.HTTP_201_CREATED)


class GetMappedPropertyTypeAPIView(viewsets.ReadOnlyModelViewSet):
    queryset = PartnerPropertyMapping.objects.all()
    serializer_class = PartnerPropertyMappingSerializer

    def get_queryset(self):
        partner_key = self.request.query_params.get('partner')
        qs = self.queryset
        if partner_key:
            qs = qs.filter(partner_property__partner__key=partner_key.upper())
        return qs

    def list(self, request, *args, **kwargs):
        querysets = self.get_queryset()
        map = {}
        for qs in querysets:
            key = qs.property_type.name
            if key in map.keys():
                map[key].update({
                    qs.partner_property.id: qs.partner_property.name
                })
            else:
                map[key] = {
                    qs.partner_property.id: qs.partner_property.name
                }
        
        result = {
            "data": map
        }
        
        return Response(data=result, status=200)


class PropertyGroupViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PropertyGroup.objects.all()
    serializer_class = PropertyGroupSerializer

    def list(self, request, *args, **kwargs):
        qs = PropertyGroup.objects.all()
        serializer = PropertyGroupSerializer(qs, many=True)
        return Response(data=serializer.data, status=200)


class PartnerProviderViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PartnerProviderSerializer
    queryset = PartnerProvider.objects.all().order_by('order')

    def list(self, request, *args, **kwargs):
        brand_key = request.query_params.get('site')
        if brand_key:
            try:
                brand = Brand.objects.get(key=brand_key.upper())
            except Exception as e:
                return Response({'error': e, 'message': 'Wrong site name'})
        else:
            return Response({'error': 'You have to pass site(brand) name.'})

        partner_key = request.query_params.get('partner')
        if partner_key:
            partner = Partner.objects.get(key=partner_key.upper())
        else:
            partner = Partner.objects.get(key='KY')

        qs_by_default_order = PartnerProvider.objects.filter(partner=partner).order_by('order')
        serializer_default_order = PartnerProviderSerializer(qs_by_default_order, many=True)
        data = defaultdict()
        data = {
            "default_order": serializer_default_order.data
        }

        locations = BrandLocationPartnerProperty.objects.filter(brand=brand, partner=partner)
        for loc in locations:
            providers_by_order = BrandLocationPartnerPropertyProvider.objects.filter(loc=loc).order_by('order')
            provider_names = [p.provider.provider_id for p in providers_by_order]
            location = loc.location
            data.setdefault(location.location_type, {}).setdefault(location.country_code, {})\
                .setdefault(loc.property_group.name, {}).setdefault(loc.device.type, {})
            data[location.location_type][location.country_code][loc.property_group.name][loc.device.type] = \
                provider_names

        return Response(data=data, status=200)


class SetWithRatioViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SiteEnableSetsES.objects.all()
    serializer_class = SetWithRatioSerializer

    def list(self, request, *args, **kwargs):
        site_key = request.query_params.get('site')
        if site_key:
            brand = Brand.objects.filter(key=site_key.upper())[0]
        else:
            brand = Brand.objects.filter(key='RBO')[0]
        location = request.query_params.get('location')
        if location:
            loc = Location.objects.filter(country_code=location.upper())[0]
        else:
            loc = None

        # ratio_group = RatioGroup.objects.all()
        # sets_by_site_name = SiteEnableSet.objects.filter(active=True, site__key__icontains=site_key)

        qs = BrandLocationDefinedSetsRatio.objects.filter(brand=brand)
        defined_data = {}
        location_data = {}
        for rs in qs:
            defined_data.setdefault("brand_defined_sets_ratio", {}).setdefault(rs.property_group.name, {})\
                .setdefault(rs.device.type, {})
            defined_data['brand_defined_sets_ratio'][rs.property_group.name][rs.device.type] = \
                {r.partner.feed: f"{r.ratio}" for r in rs.ratio_set.get_ratio_set}

            location_data.setdefault("brand_locations_sets_ratio", {}).setdefault(rs.location.location_type, {}) \
                .setdefault(rs.location.country_code, {}).setdefault(rs.property_group.name, {})\
                .setdefault(rs.device.type, {})
            location_data['brand_locations_sets_ratio'][rs.location.location_type][rs.location.country_code][rs.property_group.name][rs.device.type] =\
                {r.partner.feed: f"{r.ratio}" for r in rs.ratio_set.get_ratio_set}

        data = {
            "brand_defined_sets_ratio": defined_data,
            "brand_locations_sets_ratio": location_data
        }

        return Response(data)


class RatioGroupViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = RatioGroup.objects.all()
    serializer_class = RatioGroupSerializer

    def list(self, request, *args, **kwargs):
        qs = RatioGroup.objects.all()
        data_list = []
        for data in qs:
            ratio_data = {data.id: RatioGroupSerializer(data).data}
            data_list.append(ratio_data)
        # serializer = RatioGroupGroupSerializer(qs, many=True)
        return Response(data=data_list, status=200)


class GetSTSConfigViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = BrandLocationDefinedSetsRatio.objects.all()

    def list(self, request, *args, **kwargs):
        start_time = time.perf_counter()
        site_key = request.query_params.get('site')
        if site_key:
            try:
                brand = Brand.objects.filter(key=site_key.upper())[0]
            except Exception as e:
                return Response({'error': 'site not exist'})
        else:
            brand = Brand.objects.filter(key='RBO')[0]

        qs = BrandLocationDefinedSetsRatio.objects.select_related("ratio_set", "property_group", "device", "location",
                                                        "brand", "search_location", "created_by").filter(brand=brand)

        es_qs = SiteEnableSetsES.objects.filter(brand=brand)
        es_serializer = SiteEnableSetsESSerializer(es_qs, many=True)
        es_data_list = es_serializer.data
        #
        es_data = {}
        for es in es_data_list:
            key = list(es.keys())[0]
            value = es[key]
            es_data.setdefault(key, [])
            es_data[key].append(value)

        data = {
            'set_list_es': es_data,
            'set_with_ratio': {}
        }

        def_qs = SiteEnableSetsES.objects.filter(brand=brand, active=1)
        def_serializer = DefaultQueryESSerializer(def_qs, many=True)
        default_es_data = def_serializer.data
        data['default_es_query'] = default_es_data[0] if default_es_data else None

        ratio = {}
        full_row_query = {}

        for rs in qs:
            ratio_dict = {r.partner.feed: f"{r.ratio}" for r in rs.ratio_set.get_ratio_set()}
            ratio.setdefault("brand_defined_sets_ratio", {}).setdefault(rs.property_group.name.lower(), {}) \
                .setdefault(rs.device.type.lower(), {})
            ratio['brand_defined_sets_ratio'][rs.property_group.name.lower()][rs.device.type.lower()] = ratio_dict

            ratio.setdefault("brand_locations_sets_ratio", {}).setdefault(rs.location.location_type, {}) \
                .setdefault(rs.location.country_code, {}).setdefault('Default', {}).setdefault(rs.property_group.name.lower(), {}) \
                .setdefault(rs.device.type.lower(), {})
            ratio['brand_locations_sets_ratio'][rs.location.location_type][rs.location.country_code]['Default'][
                rs.property_group.name.lower()][rs.device.type.lower()] = ratio_dict

            row_query = {}

            if rs.location.country_code == 'ROW':
                sl_id = rs.search_location.ep_location_id

                row_query[sl_id] = {}
                row_query[sl_id]['slug'] = rs.search_location.slug
                row_query[sl_id]['type_level'] = str(rs.search_location.type_level)
                row_query[sl_id]['location_level'] = str(rs.search_location.location_level)
                row_query[sl_id].setdefault(rs.property_group.name.lower(), {}).setdefault(rs.device.type.lower(), {})
                row_query[sl_id][rs.property_group.name.lower()][rs.device.type.lower()] = ratio_dict

            full_row_query = {**row_query}

        row = ratio['brand_locations_sets_ratio']['continent']['ROW']
        new_row = { **row, **full_row_query}
        ratio['brand_locations_sets_ratio']['continent']['ROW'] = new_row
        data['set_with_ratio']['ratio'] = ratio
        for es_fields_data in default_es_data:
            data['set_with_ratio'].setdefault('es_fields', [])
            data['set_with_ratio']['es_fields'].append(es_fields_data['es_fields'])

        end_time = time.perf_counter()
        elapsed_time = end_time - start_time
        print(f"Elapsed time: {elapsed_time:.6f} seconds")

        return Response(data)


class NewGetSTSConfigViewSetMT(viewsets.ReadOnlyModelViewSet):
    queryset = BrandLocationDefinedSetsRatio.objects.all()
    ratio_service = STSAPIService()
    # permission_classes = [IsAccountAdminOrReadOnly]

    def list(self, request, *args, **kwargs):
        site_key = request.query_params.get('site')
        from_cache = request.query_params.get('cache')

        if not site_key:
            site_key = 'RBO'

        if from_cache:
            site_response = cache.get(site_key)
            if site_response:
                return Response(site_response)

        data = self.ratio_service.get_ratio(site_key)

        cache.set(site_key, data, timeout=None)
        return Response(data)


class LeaveBehindPopUnderRulesAPIView(generics.ListAPIView):
    queryset = LeaveBehindPopUnderRules.objects.all()
    serializer_class = LeaveBehindPopUnderRulesSerializer

    def list(self, request):
        # import pdb; pdb.set_trace()
        queryset = self.get_queryset()
        serializer = LeaveBehindPopUnderRulesSerializer(queryset, many=True)
        data = serializer.data
        result_object = {k: v for item in data for k, v in item.items()}
        return Response(result_object)


class AmenityTypeRefresh(generics.ListCreateAPIView):
    queryset = AmenityTypeCategory.objects.order_by('id')
    serializer_class = AmenityTypeSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def create(self, request, *args, **kwargs):
        data = request.data if isinstance(request.data, list) else [request.data]
        serializer = self.get_serializer(data=data, many=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class AmenityTypeUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = AmenityTypeCategory.objects.order_by('id')
    serializer_class = AmenityTypeUpdateDeleteSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None
    lookup_field = 'id'


class PartnerAmenityTypeRefresh(generics.ListCreateAPIView):
    queryset = PartnerAmenityType.objects.order_by('id')
    serializer_class = PartnerAmenityTypeSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        data = request.data if isinstance(request.data, list) else [request.data]
        serializer = self.get_serializer(data=data, many=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class PartnerAmenityTypeUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PartnerAmenityType.objects.order_by('id')
    serializer_class = PartnerAmenityTypeUpdateDeleteSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None
    lookup_field = 'id'
