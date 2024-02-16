import time, json

from apps.brands.models import Brand, StaticSiteMapUrl, DynamicSiteMapUrl
from apps.sqs.models import SetListES, SiteEnableSetsES
from apps.sqs.serializers import (SetListESSerializer, ESFieldsSerializer, DefaultSetListESSerializer)
from apps.sts.models import BrandLocationDefinedSetsRatio, RatioGroup, Location, RatioSet


class STSAPIService:

    def get_ratio(self, site_key):

        if not site_key:
            site_key = 'rbo'

        try:
            brand = Brand.objects.filter(key=site_key.upper())[0]
        except Exception as e:
            data = {'error': 'site not exist'}
            return data

        qs = BrandLocationDefinedSetsRatio.objects.select_related("ratio_set", "property_group", "device", "location",
                                                                  "brand", "search_location", "created_by").filter(
            brand=brand)

        set_list_es_qs = SetListES.objects.all()
        es_serializer = SetListESSerializer(set_list_es_qs, many=True)
        es_data_list = es_serializer.data

        set_list_es_data = {}
        try:
            for es in es_data_list:
                set_list_es_data[es['name'].lower()] = [json.loads(es['es_fields'])]
        except Exception as e:
            data = json.dumps(es['es_fields'])
            set_list_es_data[es['name'].lower()] = [json.loads(data)]
            pass
            # print(e)

        data = {
            'set_list_es': set_list_es_data,
            'set_with_ratio': {}
        }
        def_qs = SetListES.objects.get(default=1)
        def_serializer = DefaultSetListESSerializer(def_qs)
        default_es_data = def_serializer.data
        data['default_es_query'] = default_es_data

        brand_es_qs = SiteEnableSetsES.objects.filter(brands__in=[brand], active=True)
        brand_es_serializer = ESFieldsSerializer(brand_es_qs, many=True)
        es_fields = brand_es_serializer.data

        ratio = {}
        default_orders = {}
        duplicate_property_partner_order = {}

        if qs:
            for rs in qs:
                # ratio_dict = {r.partner.feed: f"{r.ratio}" for r in rs.ratio_set.get_ratio_set()}
                ratio_dict = {}
                vrbos = []
                for r in rs.ratio_set.get_ratio_set():
                    if r.partner.feed == 12:
                        vrbos.append(f"{r.ratio}")
                    else:
                        ratio_dict[r.partner.feed] = f"{r.ratio}"
                if vrbos:
                    ratio_dict[12] = {i: v for i, v in enumerate(vrbos)}

                # Update brand_defined_sets_ratio
                ratio.setdefault("brand_defined_sets_ratio", {}).setdefault(rs.property_group.name.lower(), {}) \
                    .setdefault(rs.device.type.lower(), {})
                ratio['brand_defined_sets_ratio'][rs.property_group.name.lower()][rs.device.type.lower()] = ratio_dict

                # Update brand_locations_sets_ratio
                (ratio.setdefault("brand_locations_sets_ratio", {}).setdefault(rs.location.location_type, {})
                    .setdefault(rs.location.country_code, {}).setdefault(rs.search_location.ep_location_id, {})
                    .setdefault(rs.property_group.name.lower(), {}).setdefault(rs.device.type.lower(), {}))

                ep_location_id = rs.search_location.ep_location_id

                # ratio['brand_locations_sets_ratio'][rs.location.location_type][rs.location.country_code][
                #     ep_location_id] = {}
                ratio['brand_locations_sets_ratio'][rs.location.location_type][rs.location.country_code][
                    ep_location_id]['slug'] = rs.search_location.slug
                ratio['brand_locations_sets_ratio'][rs.location.location_type][rs.location.country_code][
                    ep_location_id]['type_level'] = str(rs.search_location.type_level) if (
                    rs.search_location.type_level) else rs.search_location.type_level
                ratio['brand_locations_sets_ratio'][rs.location.location_type][rs.location.country_code][
                    ep_location_id]['location_level'] = str(rs.search_location.location_level) if (
                    rs.search_location.location_level) else rs.search_location.location_level

                ratio['brand_locations_sets_ratio'][rs.location.location_type][rs.location.country_code][
                    rs.search_location.ep_location_id][rs.property_group.name.lower()][rs.device.type.lower()] = ratio_dict

                # if rs.location.country_code == 'ROW':
                #     ratio['brand_locations_sets_ratio'][rs.location.location_type][rs.location.country_code][
                #         ep_location_id] = {}
                #     ratio['brand_locations_sets_ratio'][rs.location.location_type][rs.location.country_code][
                #         ep_location_id]['slug'] = rs.search_location.slug
                #     ratio['brand_locations_sets_ratio'][rs.location.location_type][rs.location.country_code][
                #         ep_location_id]['type_level'] = str(rs.search_location.type_level)
                #     ratio['brand_locations_sets_ratio'][rs.location.location_type][rs.location.country_code][
                #         ep_location_id]['location_level'] = str(rs.search_location.location_level)
                #     ratio['brand_locations_sets_ratio'][rs.location.location_type][rs.location.country_code][
                #         ep_location_id].setdefault(rs.property_group.name.lower(), {}).setdefault(
                #         rs.device.type.lower(), {})
                #     ratio['brand_locations_sets_ratio'][rs.location.location_type][rs.location.country_code][
                #         ep_location_id][rs.property_group.name.lower()][rs.device.type.lower()] = ratio_dict
                # else:
                #
                #     ratio['brand_locations_sets_ratio'][rs.location.location_type][rs.location.country_code][
                #         ep_location_id][rs.property_group.name.lower()][rs.device.type.lower()] = ratio_dict
                partners = rs.duplicatepropertypartnerorder_set.all().order_by("order")
                if partners:
                    partner_orders = [p.partner.key if p.partner.feed != 12 else 'HA' for p in partners]
                    duplicate_property_partner_order.setdefault(rs.location.location_type, {})\
                        .setdefault(rs.location.country_code, {}).setdefault(rs.property_group.name.lower(), {})\
                        .setdefault(rs.device.type.lower(), {})

                    if (rs.location.country_code == 'ROW' and rs.property_group.name.lower() == 'default' and
                            rs.device.type.lower() == 'desktop'):
                        duplicate_property_partner_order.setdefault('default_order', [])
                        duplicate_property_partner_order['default_order'] = partner_orders

                    duplicate_property_partner_order[rs.location.location_type][rs.location.country_code][
                        rs.property_group.name.lower()][
                        rs.device.type.lower()] = partner_orders

            row = ratio['brand_locations_sets_ratio']['continent'].get('ROW', '')

            ratio['brand_locations_sets_ratio']['continent']['ROW'] = row

        data['set_with_ratio']['ratio'] = ratio
        data['duplicate_property_partner_order'] = duplicate_property_partner_order

        ids = []
        for es_fields_data in es_fields:
            data['set_with_ratio'].setdefault('es_fields', [])
            ids.append(str(es_fields_data.pop("id")))
            data['set_with_ratio']['es_fields'].append(es_fields_data)

        data['set_with_ratio']['tweaks_es'] = ", ".join(ids)

        return data
