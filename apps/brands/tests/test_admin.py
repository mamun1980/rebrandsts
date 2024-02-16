import datetime
from django.contrib.auth.models import User
from django.utils.timezone import make_aware
from django.contrib.admin.sites import AdminSite
from django.test import TestCase, Client, RequestFactory

from apps.brands.filters import BrandFilter
from apps.partners.filters import PartnerFilter
from apps.partners.models import Partner, Provider
from apps.brands.models import Brand, BrandsPartners, BrandsProviders
from apps.brands.admin import BrandAdmin, BrandsPartnersAdmin, BrandsProvidersAdmin


class SetUpClass(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.request_factory = RequestFactory()
        cls.username = 'admin'
        cls.password = 'adminpassword'

        user = User.objects.create_superuser(
            username='admin',
            password='adminpassword',
            email='admin@example.com'
        )
        cls.user = user


class BrandAdminTestCase(SetUpClass):

    def setUp(self):
        self.client = Client()
        self.client.login(username=self.username, password=self.password)
        self.site = AdminSite()
        self.model_admin = BrandAdmin(Brand, self.site)
        self.brand1 = Brand.objects.create(
            id=1,
            name="This is a test brand one",
            alias="This is a test brand alias one",
            key='TB1',
            date=make_aware(datetime.datetime.now()),
            sort_order=1
        )

        self.brand2 = Brand.objects.create(
            id=2,
            name="This is a test brand two",
            alias="This is a test brand alias two",
            key='TB2',
            date=make_aware(datetime.datetime.now()),
            sort_order=2
        )

    @classmethod
    def tearDownClass(cls):
        Brand.objects.all().delete()
        Partner.objects.all().delete()
        BrandsPartners.objects.all().delete()
        User.objects.all().delete()

    def test_save_model_method_in_brand_admin(self):
        obj = Brand(name='Test Brand', alias='Test Brand', key='TB')
        request = self.request_factory.post('/admin/brands/brand/add/')
        request.user = self.user

        # Call the save_model method
        self.model_admin.save_model(request, obj, None, None)

        # Retrieve the object from the database to check if it was saved
        saved_obj = Brand.objects.get(pk=obj.pk)

        # Assert that the object was saved correctly
        self.assertEqual(saved_obj.name, 'Test Brand')
        self.assertEqual(saved_obj.alias, 'Test Brand')
        self.assertEqual(saved_obj.key, 'TB')
        self.assertIsNotNone(obj.id)
        self.assertEqual(obj.created_by, self.user)

    def test_update_brand_data(self):
        obj = Brand.objects.get(id=self.brand1.id)
        obj.name = 'Test Brand'
        url = f'/admin/brands/brand/{self.brand1.id}/change/'
        request = self.request_factory.post(url)
        request.user = self.user
        self.model_admin.save_model(request, obj, None, None)
        # Retrieve the object from the database to check if it was saved
        update_obj = Brand.objects.get(id=self.brand1.id)
        # Assert that the object was saved correctly
        self.assertEqual(update_obj.name, 'Test Brand')

    def test_delete_brand_data(self):
        obj = Brand(name='Test Brand', alias='Test Brand', key='TB')
        request = self.request_factory.post('/admin/brands/brand/add/')
        request.user = self.user
        # Call the save_model method
        self.model_admin.save_model(request, obj, None, None)

        # Retrieve the object from the database to check if it was saved
        saved_obj = Brand.objects.get(pk=obj.pk)
        self.assertEqual(saved_obj.name, 'Test Brand')
        self.model_admin.delete_model(self.client, saved_obj)
        with self.assertRaises(Brand.DoesNotExist):
            Brand.objects.get(pk=obj.pk)

    def test_show_partners(self):
        brand = Brand.objects.create(id=3, name='Test Brand', key='test_key', sort_order=1, alias='test_alias',
                                     date=make_aware(datetime.datetime.now()))
        partner1 = Partner.objects.create(id=1, name='Partner 1')
        partner2 = Partner.objects.create(id=2, name='Partner 2')
        BrandsPartners.objects.create(brand=brand, partner=partner1)
        BrandsPartners.objects.create(brand=brand, partner=partner2)

        brand_admin = BrandAdmin(Brand, self.site)
        result = brand_admin.show_partners(brand)

        self.assertEqual(result, 'Partner 1, Partner 2')

    def test_list_display_and_ordering(self):
        expected_list_display = ['id', 'name', 'key', 'sort_order', 'alias', 'show_partners', 'date']
        self.assertEqual(self.model_admin.list_display, expected_list_display)
        self.assertEqual(self.model_admin.ordering, ['-updated_at', 'id'])

    def test_search_fields(self):
        brand_admin = BrandAdmin(Brand, self.site)
        self.assertEqual(brand_admin.search_fields, ['name', 'key', 'alias'])


class BrandsPartnersAdminTestCase(SetUpClass):

    def setUp(self):
        self.client = Client()
        self.client.login(username=self.username, password=self.password)
        self.site = AdminSite()
        self.model_admin = BrandsPartnersAdmin(BrandsPartners, self.site)
        self.brand = Brand.objects.create(
            id=1,
            name="This is a test brand one",
            alias="This is a test brand alias one",
            key='TB1',
            date=make_aware(datetime.datetime.now()),
            sort_order=1
        )
        self.partner = Partner.objects.create(id=1, name='Partner 1')
        self.brands_partners = BrandsPartners.objects.create(brand=self.brand, partner=self.partner)

    @classmethod
    def tearDownClass(cls):
        Brand.objects.all().delete()
        Partner.objects.all().delete()
        User.objects.all().delete()

    def test_list_display(self):
        # Test if the list display attributes are set correctly
        self.assertEqual(self.model_admin.list_display, ['brand', 'partner'])

    def test_list_filter(self):
        # Test if the list filter attributes are set correctly
        self.assertEqual(self.model_admin.list_filter, [BrandFilter, PartnerFilter])

    def test_save_model_method_in_brand_admin(self):
        brand = Brand.objects.create(id=2, name='Test Brand', alias='Test Brand', key='TB')
        partner = Partner.objects.create(id=2, name='Test Partner 1', key='TP1', domain_name='testpartner.com', feed=11)
        brands_partner = BrandsPartners(id=1, brand=brand, partner=partner)

        request = self.request_factory.post('/admin/brands/brandspartners/add/')
        request.user = self.user

        # Call the save_model method
        self.model_admin.save_model(request, brands_partner, None, None)

        # Retrieve the object from the database to check if it was saved
        saved_obj = BrandsPartners.objects.get(pk=brands_partner.pk)

        # Assert that the object was saved correctly
        self.assertEqual(saved_obj.brand.name, 'Test Brand')
        self.assertEqual(saved_obj.partner.name, 'Test Partner 1')

    def test_brands_partners_admin_change_view(self):
        brand2 = Brand.objects.create(id=2, name='Another Brand')
        partner2 = Partner.objects.create(id=2, name='Another Partner')

        response = self.client.post(
            f'/admin/brands/brandspartners/{self.brands_partners.id}/change/',
            {
                'brand': brand2.id,
                'partner': partner2.id,
            }
        )

        # Check if the BrandsPartners instance is modified successfully
        self.assertEqual(response.status_code, 302)  # HTTP redirect status code indicating success
        self.brands_partners.refresh_from_db()
        self.assertEqual(self.brands_partners.brand, brand2)

    def test_brands_partners_admin_delete_view(self):
        response = self.client.post(
            f'/admin/brands/brandspartners/{self.brands_partners.id}/delete/',
            {'post': 'yes'},
        )

        # Check if the BrandsPartners instance is deleted successfully
        self.assertEqual(response.status_code, 302)  # HTTP redirect status code indicating success
        self.assertEqual(BrandsPartners.objects.count(), 0)


class BrandsProvidersAdminTestCase(SetUpClass):

    def setUp(self):
        self.client = Client()
        self.client.login(username=self.username, password=self.password)
        self.site = AdminSite()
        self.model_admin = BrandsProvidersAdmin(BrandsProviders, self.site)
        self.brand = Brand.objects.create(
            id=1,
            name="This is a test brand one",
            alias="This is a test brand alias one",
            key='TB1',
            date=make_aware(datetime.datetime.now()),
            sort_order=1
        )
        self.provider = Provider.objects.create(id=1, name='provider 1')
        self.brands_provider = BrandsProviders.objects.create(brand=self.brand, provider=self.provider)

    @classmethod
    def tearDownClass(cls):
        Brand.objects.all().delete()
        Provider.objects.all().delete()
        User.objects.all().delete()

    def test_list_display(self):
        # Test if the list display attributes are set correctly
        self.assertEqual(self.model_admin.list_display, ['brand', 'provider'])

    def test_brands_providers_admin_list_view(self):
        response = self.client.get('/admin/brands/brandsproviders/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This is a test brand one')
        self.assertContains(response, 'provider 1')

    def test_brands_providers_admin_add_view(self):
        brand2 = Brand.objects.create(
            id=2, name="This is a test brand two",
            alias="This is a test brand alias two",
            key='TB2',
            date=make_aware(datetime.datetime.now()),
            sort_order=1
        )
        provider2 = Provider.objects.create(id=2, provider_id='another_provider', name='Another Provider')

        response = self.client.post(
            '/admin/brands/brandsproviders/add/',
            {
                'brand': brand2.id,
                'provider': provider2.id,
            }
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(BrandsProviders.objects.count(), 2)

    def test_brands_providers_admin_change_view(self):
        brand2 = Brand.objects.create(id=2, name='Another Brand')
        provider2 = Provider.objects.create(id=2, provider_id='another_provider', name='Another Provider')

        response = self.client.post(
            f'/admin/brands/brandsproviders/{self.brands_provider.id}/change/',
            {
                'brand': brand2.id,
                'provider': provider2.id,
            }
        )

        # Check if the BrandsProviders instance is modified successfully
        self.assertEqual(response.status_code, 302)
        self.brands_provider.refresh_from_db()
        self.assertEqual(self.brands_provider.brand, brand2)

    def test_brands_providers_admin_delete_view(self):
        response = self.client.post(
            f'/admin/brands/brandsproviders/{self.brands_provider.id}/delete/',
            {'post': 'yes'},
        )

        # Check if the BrandsProviders instance is deleted successfully
        self.assertEqual(response.status_code, 302)
        self.assertEqual(BrandsProviders.objects.count(), 0)
