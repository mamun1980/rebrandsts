import json
import datetime
import base64
from rest_framework.test import APITestCase, APIClient
from apps.property.models import (
    PartnerPropertyMapping, PropertyGroup, Partner, PropertyType, PartnerPropertyType
)
from apps.brands.models import Brand
from apps.sts.models import RatioSet, BrandLocationDefinedSetsRatio, Device, Location, SearchLocation
from apps.sqs.models import SetListES, SiteEnableSetsES
from django.contrib.auth.models import User
from rest_framework import status
from django.urls import reverse
from django.utils.timezone import make_aware


class PartnerAPIViewTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.partner = Partner.objects.create(
            id=1,
            name="Booking.com",
            key="BC",
            domain_name="booking.com",
            date="2019-04-18T15:12:42Z",
            feed=11,
            sort_order=1,
            created_at="2023-11-16T06:04:07.966000Z",
            updated_at="2023-11-16T06:04:07.966000Z"
        )

    @classmethod
    def tearDownClass(cls):
        Partner.objects.all().delete()

    def test_partner_list_api(self):
        url = "/api/partners/"
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data.get('count'), 1)
        self.assertEqual(data.get('results')[0].get('name'), 'Booking.com')

    def test_get_partner_by_id_api(self):
        url = f"/api/partners/{self.partner.id}/"
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data.get('name'), 'Booking.com')
        self.assertEqual(data.get('key'), 'BC')


class RatioSetAPIViewTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.username = 'admin'
        cls.password = 'adminpassword'

        user = User.objects.create_superuser(
            username='admin',
            password='adminpassword',
            email='admin@example.com'
        )
        cls.user = user

        cls.ratio_set1 = RatioSet.objects.create(
            id=2,
            title="VRBO=80%, BC=15%, AB=5%",
            ratio_location=None
        )
        cls.ratio_set2 = RatioSet.objects.create(
            id=3,
            title="VRBO=5%, BC=75%, AB=20%",
            ratio_location=None
        )

    def setUp(self):
        # Your setup code, if any
        self.client = APIClient()

    def get_basic_auth_header(self):
        return 'Basic ' + base64.b64encode(f'{self.username}:{self.password}'.encode('utf-8')).decode('utf-8')

    @classmethod
    def tearDownClass(cls):
        RatioSet.objects.all().delete()
        User.objects.all().delete()

    def test_ratio_set_list_api(self):
        url = reverse('ratioset-list')
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data.get('count'), 2)
        self.assertEqual(data.get('results')[0].get('title'), 'VRBO=80%, BC=15%, AB=5%')

    def test_add_ratio_set_api(self):
        url = reverse('ratioset-list')
        headers = {'Content-Type': 'application/json'}
        data = {
            "title": "HA=20%, BC=40%, AB=40%",
            "ratio_location": None,
        }

        response = self.client.post(
            path=url,
            data=data,
            format='json',
            HTTP_AUTHORIZATION=self.get_basic_auth_header(),
            headers=headers
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data.get('title'), "HA=20%, BC=40%, AB=40%")

    def test_update_ratio_set(self):
        detail_url = reverse('ratioset-detail', args=[self.ratio_set2.id])
        headers = {'Content-Type': 'application/json'}
        updated_data = {'title': 'Updated Ratio Set'}
        response = self.client.put(
            detail_url,
            data=updated_data,
            format='json',
            HTTP_AUTHORIZATION=self.get_basic_auth_header(),
            headers=headers
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated Ratio Set')

    def test_delete_ratio_set_api(self):
        detail_url = reverse('ratioset-detail', args=[self.ratio_set2.id])
        response = self.client.delete(detail_url, HTTP_AUTHORIZATION=self.get_basic_auth_header())
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(RatioSet.objects.filter(id=self.ratio_set2.id).exists())


class GetMappedPropertyTypeAPITest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.username = 'admin'
        cls.password = 'adminpassword'

        cls.user = User.objects.create_superuser(
            username='admin',
            password='adminpassword',
            email='admin@gmail.com'
        )
        partner = Partner.objects.create(
            id=1,
            name='Test Partner',
            key='TC1',
            domain_name='testpartner1.com',
            feed=11
        )
        property_group = PropertyGroup.objects.create(
            id=1,
            name='Group A',
            property_ordering=2
        )
        brand = Brand.objects.create(
            id=1,
            name='Test Brand One',
            alias='Test Brand 1',
            key='TB1',
            date=make_aware(datetime.datetime.now())
        )
        brand.partners.set([partner.id])

        property_types = PropertyType.objects.create(
            id=1,
            name='Type A',
            brand_type='rentals'
        )
        property_types.accommodation_type.set([property_group.id])
        partner_property_types = PartnerPropertyType.objects.create(
            id=1,
            name='Property Type A',
            partner=partner
        )

        partner_property_mapping = PartnerPropertyMapping.objects.create(
            property_type=property_types,
            partner_property=partner_property_types
        )
        cls.partner_property_mapping = partner_property_mapping

    def setUp(self):
        self.client = APIClient()

    @classmethod
    def tearDownClass(cls):
        User.objects.all().delete()
        Partner.objects.all().delete()
        PropertyGroup.objects.all().delete()
        Brand.objects.all().delete()
        PropertyType.objects.all().delete()
        PartnerPropertyType.objects.all().delete()
        PartnerPropertyMapping.objects.all().delete()

    def get_basic_auth_header(self):
        return 'Basic ' + base64.b64encode(f'{self.username}:{self.password}'.encode('utf-8')).decode('utf-8')

    def test_get_partner_property_mapping(self):
        url = '/api/get-mapped-property-types/'
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data), 1)
        self.assertEqual(data, {'data': {'Type A': {'1': 'Property Type A'}}})
    def test_get_partner_property_mapping_by_partner_key(self):
        url = '/api/get-mapped-property-types/?partner=TC1'
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data), 1)
        self.assertEqual(data, {'data': {'Type A': {'1': 'Property Type A'}}})


class PropertyTypeRefressAPITest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.username = 'admin'
        cls.password = 'adminpassword'

        cls.user = User.objects.create_superuser(
            username='admin',
            password='adminpassword',
            email='admin@gmail.com'
        )
        partner = Partner.objects.create(
            id=1,
            name='Test Partner',
            key='TC1',
            domain_name='testpartner1.com',
            feed=11
        )
        property_types = PropertyType.objects.create(
            id=1,
            name='Type A',
            brand_type='rentals'
        )

        partner_property_types = PartnerPropertyType.objects.create(
            id=1,
            name='Property Type A',
            partner=partner
        )
        cls.property_types = property_types
        cls.partner_property_types = partner_property_types

    def setUp(self):
        self.client = APIClient()

    @classmethod
    def tearDownClass(cls):
        User.objects.all().delete()
        Partner.objects.all().delete()
        PropertyGroup.objects.all().delete()
        Brand.objects.all().delete()
        PropertyType.objects.all().delete()
        PartnerPropertyType.objects.all().delete()
        PartnerPropertyMapping.objects.all().delete()

    def get_basic_auth_header(self):
        return 'Basic ' + base64.b64encode(f'{self.username}:{self.password}'.encode('utf-8')).decode('utf-8')

    def test_add_partner_property_mapping(self):
        url = '/api/property-type-refresh/'
        headers = {'Content-Type': 'application/json'}
        response = self.client.post(
            url,
            data={
                "11": [
                    "Aparthotels-test",
                    "Chalets-test"
                ]
            },
            format='json',
            HTTP_AUTHORIZATION=self.get_basic_auth_header(),
            headers=headers

        )
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(data), 2)
        self.assertEqual(data.get('status'), 'Success')


class GetSTSConfigTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.username = 'admin'
        cls.password = 'adminpassword'

        user = User.objects.create_superuser(
            username='admin',
            password='adminpassword',
            email='admin@example.com'
        )
        cls.user = user
        ratio_set = RatioSet.objects.create(
            id=1,
            title='VRBO=80%, BC=15%, AB=5%',
            ratio_title=None,
            ratio_location=None
        )
        property_group = PropertyGroup.objects.create(
            id=1,
            name='Default',
            property_ordering=0
        )
        partner = Partner.objects.create(
            id=1,
            name='Booking.com',
            key='BC',
            domain_name='booking.com',
            feed=11,
            sort_order=1
        )
        brand = Brand.objects.create(
            id=1,
            name='RentalHomes.com',
            alias='RENTALHOMES',
            key='RBO',
            sort_order=14
        )
        brand.partners.set([partner.id])

        brand1 = Brand.objects.create(
            id=2,
            name='PetFriendly.io',
            alias='PETFRIENDLY',
            key='PET',
            sort_order=10
        )
        brand1.partners.set([partner.id])

        property_types = PropertyType.objects.create(
            id=1,
            name='Apartment',
            brand=brand,
            brand_type='rentals'
        )
        property_types.accommodation_type.set([property_group.id])

        location = Location.objects.create(
            id=1,
            location_type='continent',
            country_code='ROW',
            country='ROW/Default'
        )
        search_location = SearchLocation.objects.create(
            id=1,
            search_location='Default',
            place_id='Default',
            sort_order=1,
            ep_location_id='Default',
            location_type=None,
            type_level=None,
            slug=None,
            location_level=None
        )
        device = Device.objects.create(
            id=1,
            type='Desktop',
            sort_order=1
        )
        set_list_es = SetListES.objects.create(
            id=1,
            name='default es query',
            description=' ',
            es_fields='{"sort": [{"feed_provider_quality_score": {"order": "desc"}}]}',
            default=1,
            index_name='rental_properties,rp'
        )
        site_enable_sets_es = SiteEnableSetsES.objects.create(
            id=1,
            set_list=set_list_es,
            active=True
        )
        site_enable_sets_es.brands.set([brand.id, brand1.id])

        brand_location_defined_sets_ratio = BrandLocationDefinedSetsRatio.objects.create(
            ratio_set=ratio_set,
            device=device,
            location=location,
            brand=brand,
            ratio_set_title='VRBO_70% HG_10% EP_10% BC_10% ',
            search_location=search_location,
            created_by=user,
            property_group=property_group

        )
        cls.brand_location_defined_sets_ratio = brand_location_defined_sets_ratio

    @classmethod
    def tearDownClass(cls):
        User.objects.all().delete()
        Brand.objects.all().delete()
        Device.objects.all().delete()
        Partner.objects.all().delete()
        Location.objects.all().delete()
        RatioSet.objects.all().delete()
        SetListES.objects.all().delete()
        PropertyType.objects.all().delete()
        PropertyGroup.objects.all().delete()
        SearchLocation.objects.all().delete()
        SiteEnableSetsES.objects.all().delete()
        BrandLocationDefinedSetsRatio.objects.all().delete()

    def setUp(self):
        self.client = APIClient()

    def get_basic_auth_header(self):
        return 'Basic ' + base64.b64encode(f'{self.username}:{self.password}'.encode('utf-8')).decode('utf-8')

    def test_get_sts_config(self):
        url = "/api/get-sts-config/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_sts_config_by_site(self):
        url = "/api/get-sts-config/?site=PET"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


