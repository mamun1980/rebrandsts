import datetime

from django.test import TestCase
from apps.partners.models import Partner, Provider, PartnerProvider


class PartnerModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):

        partner = Partner.objects.create(
            id=1,
            name='testpartnet1',
            key='TP1',
            domain_name='example.com',
            feed=10,
            sort_order=1
        )

        cls.partner = partner


    @classmethod
    def tearDownClass(cls):
        Partner.objects.all().delete()

    def test_model_content(self):
        self.assertEqual(self.partner.name, "testpartnet1")


class ProviderModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):

        provider = Provider.objects.create(
            provider_id=1,
            name='testprovider'
        )

        cls.provider = provider


    @classmethod
    def tearDownClass(cls):
        Provider.objects.all().delete()

    def test_model_content(self):
        self.assertEqual(self.provider.name, "testprovider")


class PartnerProviderModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        pv1 = Provider.objects.create(
            provider_id=1,
            name='testprovider1'
        )
        pv2 = Provider.objects.create(
            provider_id=2,
            name='testprovider2'
        )
        pt1 = Partner.objects.create(
            id=1,
            name='testpartnet1',
            key='TP1',
            domain_name='example.com',
            feed=10,
            sort_order=1
        )
        pt2 = Partner.objects.create(
            id=2,
            name='testpartnet2',
            key='TP2',
            domain_name='example2.com',
            feed=11,
            sort_order=2
        )

        pp = PartnerProvider.objects.create(
            partner=pt1,
            provider=pv1,
            order=1,
            is_active=True

        )


        cls.pp = pp


    @classmethod
    def tearDownClass(cls):
        Provider.objects.all().delete()
        Partner.objects.all().delete()
        PartnerProvider.objects.all().delete()

    def test_model_content(self):
        self.assertEqual(self.pp.order, 1)