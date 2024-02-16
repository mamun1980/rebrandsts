import datetime
from django.utils.timezone import make_aware
from django.test import TestCase
from apps.partners.models import Partner, Provider
from apps.brands.models import Brand, BrandsPartners, BrandsProviders, StaticSiteMapUrl, DynamicSiteMapUrl


class BrandModelTest(TestCase):

    def setUp(self):
        self.p1 = Partner.objects.create(
            id=1,
            name='testpartner1',
            key='TP1'
        )
        self.p2 = Partner.objects.create(
            id=2,
            name='testpartner2',
            key='TP2'
        )
        self.brand_data = {
            'id': 1,
            'name': "This is a test brand",
            'alias': "This is a test brand alias",
            'key': 'TB',
            'date': make_aware(datetime.datetime.now()),
            'sort_order': 1,
        }
        self.brand = Brand.objects.create(**self.brand_data)
        self.brand.partners.add(self.p1, self.p2)

    @classmethod
    def tearDownClass(cls):
        Brand.objects.all().delete()
        Partner.objects.all().delete()

    def test_create_brand(self):
        brand_count = Brand.objects.count()
        self.assertEqual(brand_count, 1)

    def test_read_brand(self):
        brand = Brand.objects.get(id=1)
        self.assertEqual(brand.name, "This is a test brand")

    def test_update_brand(self):
        updated_name = "Updated Test Brand"
        self.brand.name = updated_name
        self.brand.save()
        updated_brand = Brand.objects.get(id=1)
        self.assertEqual(updated_brand.name, updated_name)

    def test_delete_brand(self):
        brand_count_before_delete = Brand.objects.count()
        self.brand.delete()
        brand_count_after_delete = Brand.objects.count()
        self.assertEqual(brand_count_after_delete, brand_count_before_delete - 1)

    def test_positive_relation_with_partner(self):
        partners = self.brand.partners.all()
        self.assertEqual(partners.count(), 2)
        self.assertIn(self.p1, partners)
        self.assertIn(self.p2, partners)

    def test_negative_relation_with_partner(self):
        partner_not_associated = Partner.objects.create(
            id=3,
            name='testpartner3',
            key='TP3'
        )
        partners = self.brand.partners.all()
        self.assertNotIn(partner_not_associated, partners)


class BrandsPartnersModelTest(TestCase):
    def setUp(self):
        self.p1 = Partner.objects.create(
            id=1,
            name='testpartner1',
            key='TP1'
        )
        self.p2 = Partner.objects.create(
            id=2,
            name='testpartner2',
            key='TP2'
        )
        self.brand_data = {
            'id': 1,
            'name': "This is a test brand",
            'alias': "This is a test brand alias",
            'key': 'TB',
            'date': make_aware(datetime.datetime.now()),
            'sort_order': 1,
        }
        self.brand = Brand.objects.create(**self.brand_data)

        self.brand_partner_relation = BrandsPartners.objects.create(
            brand=self.brand,
            partner=self.p1
        )

    @classmethod
    def tearDownClass(cls):
        Brand.objects.all().delete()
        Partner.objects.all().delete()
        BrandsPartners.objects.all().delete()

    def test_create_brandspartners_relation(self):
        relation_count = BrandsPartners.objects.count()
        self.assertEqual(relation_count, 1)

    def test_read_brandspartners_relation(self):
        relation = BrandsPartners.objects.get(brand=self.brand, partner=self.p1)
        self.assertEqual(relation.brand, self.brand)
        self.assertEqual(relation.partner, self.p1)

    def test_update_brandspartners_relation(self):
        updated_partner = Partner.objects.create(
            id=3,
            name='testpartner3',
            key='TP3'
        )
        self.brand_partner_relation.partner = updated_partner
        self.brand_partner_relation.save()
        updated_relation = BrandsPartners.objects.get(brand=self.brand, partner=updated_partner)
        self.assertEqual(updated_relation.partner, updated_partner)

    def test_delete_brandspartners_relation(self):
        relation_count_before_delete = BrandsPartners.objects.count()
        self.brand_partner_relation.delete()
        relation_count_after_delete = BrandsPartners.objects.count()
        self.assertEqual(relation_count_after_delete, relation_count_before_delete - 1)


class BrandsProvidersModelTest(TestCase):
    def setUp(self):
        self.provider = Provider.objects.create(
            provider_id='P1',
            name='Test Provider'
        )
        self.brand_data = {
            'id': 1,
            'name': "This is a test brand",
            'alias': "This is a test brand alias",
            'key': 'TB',
            'date': make_aware(datetime.datetime.now()),
            'sort_order': 1,
        }
        self.brand = Brand.objects.create(**self.brand_data)

        self.brand_provider_relation = BrandsProviders.objects.create(
            brand=self.brand,
            provider=self.provider
        )

    @classmethod
    def tearDownClass(cls):
        Brand.objects.all().delete()
        Provider.objects.all().delete()
        BrandsProviders.objects.all().delete()

    def test_create_brandsproviders_relation(self):
        relation_count = BrandsProviders.objects.count()
        self.assertEqual(relation_count, 1)

    def test_read_brandsproviders_relation(self):
        relation = BrandsProviders.objects.get(brand=self.brand, provider=self.provider)
        self.assertEqual(relation.brand, self.brand)
        self.assertEqual(relation.provider, self.provider)

    def test_update_brandsproviders_relation(self):
        updated_provider = Provider.objects.create(
            provider_id='P2',
            name='Updated Provider'
        )
        self.brand_provider_relation.provider = updated_provider
        self.brand_provider_relation.save()
        updated_relation = BrandsProviders.objects.get(brand=self.brand, provider=updated_provider)
        self.assertEqual(updated_relation.provider, updated_provider)

    def test_delete_brandsproviders_relation(self):
        relation_count_before_delete = BrandsProviders.objects.count()
        self.brand_provider_relation.delete()
        relation_count_after_delete = BrandsProviders.objects.count()
        self.assertEqual(relation_count_after_delete, relation_count_before_delete - 1)

