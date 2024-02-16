import datetime
from django.test import TestCase
from apps.brands.models import Brand
from apps.brands.forms import BrandForm
from apps.partners.models import Partner
from django.utils.timezone import make_aware


class BrandFormTest(TestCase):
    def setUp(self):
        # Create a test partner for the form
        partner = Partner.objects.create(
            id=1,
            name='Test Partner',
            key='TP1',
            domain_name='testpartner1.com',
            date=make_aware(datetime.datetime.now()),
            feed=11
        )
        # Create a test brand for the view
        brand = Brand.objects.create(
            id=1,
            name='Test Brand One',
            alias='Test Brand 1',
            key='TB1',
            date=make_aware(datetime.datetime.now())
        )
        brand.partners.set([partner.id])
        self.brand = brand
        self.partner = partner

    def test_brand_form_valid_with_valid_data(self):
        form_data = {
            'id': 2,
            'name': 'Test Brand',
            'alias': 'Test Brand alias',
            'key': 'TB',
            'date': make_aware(datetime.datetime.now()),
            'partners': [self.partner.id]
        }
        form = BrandForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_brand_form_invalid_with_missing_data(self):
        # Test the form with missing required fields
        form_data = {}
        form = BrandForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
        self.assertIn('partners', form.errors)

    def test_brand_form_invalid_with_invalid_data(self):
        # Test the form with invalid data (e.g., invalid partner ID)
        form_data = {
            'id': 3,
            'name': 'Test Brand',
            'alias': 'Test Brand alias',
            'key': 'TB',
            'partners': [999]  # Assuming there is no partner with ID 999
        }
        form = BrandForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('partners', form.errors)

