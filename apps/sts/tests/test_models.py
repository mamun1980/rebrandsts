from django.test import TestCase
from decouple import config
import requests
from apps.property.models import PropertyGroup
import datetime
from apps.sts.models import *


class DeviceModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        device = Device.objects.create(id=1, type='Mobile')
        cls.device = device

    @classmethod
    def tearDownClass(cls):
        Device.objects.all().delete()

    def test_device_added_successfully(self):
        self.assertEqual(self.device.type, 'Mobile')


class LocationModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        location = Location.objects.create(
            id=1,
            location_type='continent',
            country_code='EU',
            country='Europe'
        )
        cls.location = location

    @classmethod
    def tearDownClass(cls):
        Location.objects.all().delete()

    def test_device_added_successfully(self):
        self.assertTrue(Location.objects.filter(country='Europe').exists())
        self.assertEqual(self.location.location_type, 'continent')
        self.assertEqual(self.location.country_code, 'EU')
        self.assertEqual(self.location.country, 'Europe')


class SearchLocationModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        token = config('TOKEN')
        corn_api_base_url = config('COMMON_CORN_API_BASE_URL')
        location_api_base_url = config('LOCATION_API_BASE_URL')
        cls.token = token
        cls.corn_api_base_url = corn_api_base_url
        cls.location_api_base_url = location_api_base_url

    @classmethod
    def tearDownClass(cls):
        SearchLocation.objects.all().delete()
        LocationType.objects.all().delete()

    def test_search_location_added_successfully(self):
        search_location = 'Paris, France'
        location_api_url = f"{self.location_api_base_url}/v1/location?keyword={search_location}"
        location_api_response = requests.get(location_api_url)
        location_data = location_api_response.json()
        location_id = location_data['GeoInfo']['LocationID']
        corn_api_url = f"{self.corn_api_base_url}/api/v1/location-info/{location_id}/?format=json&token={self.token}"
        common__corn_api_response = requests.get(corn_api_url)

        if common__corn_api_response.status_code == 200:
            common_corn_data = common__corn_api_response.json()['data']
            location_type = common_corn_data.get('location_type')
            location_type_obj, created = LocationType.objects.get_or_create(name=location_type)
            location_level = common_corn_data.get('location_level')
            type_level = common_corn_data.get('type_level')
            google_place_id = common_corn_data.get('google_place_id')

            SearchLocation.objects.create(
                id=1,
                search_location=search_location,
                place_id=google_place_id,
                sort_order=1,
                ep_location_id=location_id,
                location_level=location_level,
                location_type=location_type_obj,
                type_level=type_level,
                slug=slugify(search_location),
            )
        self.assertTrue(SearchLocation.objects.filter(search_location='Paris, France').exists())


class RatioLocationModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        ratio_location = RatioLocation.objects.create(
            id=1,
            location_name='united states',
        )
        cls.ratio_location = ratio_location

    @classmethod
    def tearDownClass(cls):
        RatioLocation.objects.all().delete()

    def test_ratio_location_added_successfully(self):
        self.assertTrue(RatioLocation.objects.filter(location_name='united states').exists())


class RatioSetModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        ratio_set = RatioSet.objects.create(id=1)
        partner = Partner.objects.create(id=1, name='test_partner_01', key='TP')
        pr01 = PartnerRatio.objects.create(
            id=1,
            partner=partner,
            ratio=100,
            ratioset=ratio_set
        )
        ratio_set.save()
        cls.ratio_set = ratio_set

    @classmethod
    def tearDownClass(cls):
        RatioSet.objects.all().delete()
        PartnerRatio.objects.all().delete()
        Partner.objects.all().delete()

    def test_ratio_set_added_successfully(self):
        self.assertTrue(RatioSet.objects.filter(id=1).exists())
        self.assertEqual(self.ratio_set.ratio_title, 'TP_100%')


class PartnerRatioModelTests(TestCase):

    @classmethod
    def setUpClass(cls):
        ratio_set = RatioSet.objects.create(id=1)
        pr01 = PartnerRatio.objects.create(
            id=1,
            partner=Partner.objects.create(id=1, name='test_partner_01', key='TP01'),
            ratio=100,
            ratioset=ratio_set
        )
        ratio_set.save()
        cls.ratio_set = ratio_set
        cls.partner_ratio = pr01

    @classmethod
    def tearDownClass(cls):
        RatioSet.objects.all().delete()
        PartnerRatio.objects.all().delete()
        Partner.objects.all().delete()

    def test_partner_ratio_added_successfully(self):
        self.assertTrue(PartnerRatio.objects.filter(id=1).exists())
        self.assertEqual(self.partner_ratio.ratio, 100)


class RatioGroupModelTests(TestCase):

    @classmethod
    def setUpClass(cls):
        pr01 = RatioGroup.objects.create(
            id=1,
            ratio_set=RatioSet.objects.create(id=1)
        )
        cls.RatioGroup = pr01

    @classmethod
    def tearDownClass(cls):
        RatioGroup.objects.all().delete()
        RatioSet.objects.all().delete()

    def test_ratio_group_added_successfully(self):
        self.assertTrue(RatioGroup.objects.filter(id=1).exists())


class BrandLocationDefinedSetsRatioModelTests(TestCase):

    @classmethod
    def setUpClass(cls):
        token = config('TOKEN')
        corn_api_base_url = config('COMMON_CORN_API_BASE_URL')
        location_api_base_url = config('LOCATION_API_BASE_URL')

        cls.property_group = PropertyGroup.objects.create(id=1, name='Hotels')
        cls.device = Device.objects.create(id=1, type='Mobile')
        cls.location = Location.objects.create(id=1, location_type='continent', country_code='EU', country='Europe')
        cls.brand = Brand.objects.create(id=1, name="This is a test brand", alias="This is a test brand alias", key='TB',
                                     date=datetime.datetime.now(), sort_order=1)

        search_location = 'Paris, France'
        location_api_url = f"{location_api_base_url}/v1/location?keyword={search_location}"
        location_api_response = requests.get(location_api_url)
        location_data = location_api_response.json()
        location_id = location_data['GeoInfo']['LocationID']
        corn_api_url = f"{corn_api_base_url}/api/v1/location-info/{location_id}/?format=json&token={token}"
        common__corn_api_response = requests.get(corn_api_url)

        if common__corn_api_response.status_code == 200:
            common_corn_data = common__corn_api_response.json()['data']
            location_type = common_corn_data.get('location_type')
            location_type_obj, created = LocationType.objects.get_or_create(name=location_type)
            location_level = common_corn_data.get('location_level')
            type_level = common_corn_data.get('type_level')
            google_place_id = common_corn_data.get('google_place_id')

            cls.search_location=SearchLocation.objects.create(
                id=1,
                search_location=search_location,
                place_id=google_place_id,
                sort_order=1,
                ep_location_id=location_id,
                location_level=location_level,
                location_type=location_type_obj,
                type_level=type_level,
                slug=slugify(search_location),
            )

        ratio_set = RatioSet.objects.create(id=1)
        pr01 = PartnerRatio.objects.create(
            id=1,
            partner=Partner.objects.create(id=1, name='test_partner_01', key='TP01'),
            ratio=100,
            ratioset=ratio_set
        )
        ratio_set.save()
        cls.ratio_set = ratio_set
        user = User.objects.create_user(username='test', email='test@gmail.com', password='qweqwe123')
        cls.user = user

    @classmethod
    def tearDownClass(cls):
        BrandLocationDefinedSetsRatio.objects.all().delete()
        RatioSet.objects.all().delete()
        PartnerRatio.objects.all().delete()
        SearchLocation.objects.all().delete()
        LocationType.objects.all().delete()
        Brand.objects.all().delete()
        Location.objects.all().delete()
        Device.objects.all().delete()
        PropertyGroup.objects.all().delete()
        Partner.objects.all().delete()

    def test_brand_location_defained_sets_ratio_added_successfully(self):
        bldsr = BrandLocationDefinedSetsRatio.objects.create(
            id=1,
            ratio_set=self.ratio_set,
            property_group=self.property_group,
            device=self.device,
            location=self.location,
            brand=self.brand,
            search_location=self.search_location,
            created_by=self.user

        )
        self.assertTrue(BrandLocationDefinedSetsRatio.objects.filter(id=1).exists())
