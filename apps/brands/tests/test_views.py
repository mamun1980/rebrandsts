import datetime
from django.utils.timezone import make_aware
from django.test import TestCase, Client
from django.urls import reverse
from apps.brands.models import Brand, Partner
from apps.brands.forms import BrandForm
from django.contrib.auth.models import User


class BrandsListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        number_of_brands = 15
        for brand_num in range(number_of_brands):
            Brand.objects.create(id=brand_num, name=f'Brand {brand_num}')

    def setUp(self):
        self.username = 'admin'
        self.password = 'adminpassword'

        user = User.objects.create_superuser(
            username='admin',
            password='adminpassword',
            email='admin@example.com'
        )
        self.user = user
        self.client = Client()
        self.client.login(username=self.username, password=self.password)

    @classmethod
    def tearDownClass(cls):
        Brand.objects.all().delete()

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/brands/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('brands-list'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('brands-list'))
        self.assertTemplateUsed(response, 'brands/list.html')

    def test_pagination_is_ten(self):
        response = self.client.get(reverse('brands-list'))
        self.assertEqual(len(response.context['brand_list']), 10)

    def test_lists_all_brands(self):
        # Get second page and confirm it has the remaining 5 items
        response = self.client.get(reverse('brands-list') + '?page=2')
        self.assertEqual(len(response.context['brand_list']), 5)

    def test_view_ordered_by_updated_at(self):
        response = self.client.get(reverse('brands-list'))
        brands = response.context['brand_list']
        for i in range(len(brands) - 1):
            self.assertGreaterEqual(brands[i].updated_at, brands[i + 1].updated_at)


class BrandsCreateViewTest(TestCase):
    def setUp(self):

        self.username = 'admin'
        self.password = 'adminpassword'

        user = User.objects.create_superuser(
            username='admin',
            password='adminpassword',
            email='admin@example.com'
        )
        self.user = user

        self.client = Client()
        self.client.login(username=self.username, password=self.password)

        self.partner = Partner.objects.create(
            id=1,
            name='Test Partner',
            key='TP1',
            domain_name='testpartner.com',
            date=make_aware(datetime.datetime.now()),
            feed=11
        )

    @classmethod
    def tearDownClass(cls):
        Brand.objects.all().delete()
        Partner.objects.all().delete()

    def test_brand_create_view_url_exists_at_desired_location(self):
        response = self.client.get('/brands/create/')
        self.assertEqual(response.status_code, 200)

    def test_brand_create_view_accessible_by_name(self):
        response = self.client.get(reverse('brand-add'))
        self.assertEqual(response.status_code, 200)

    def test_brand_create_view_uses_correct_template(self):
        response = self.client.get(reverse('brand-add'))
        self.assertTemplateUsed(response, 'brands/add-brands.html')

    def test_brand_create_view_creates_brand(self):
        data = {
            'id': 2,
            'name': 'Test Brand Two',
            'alias': 'Test Brand 2',
            'key': 'TB2',
            'partners': [self.partner.id]
        }
        response = self.client.post(reverse('brand-add'), data)
        self.assertEqual(response.status_code, 302)

        # Check if the brand is created in the database
        created_brand = Brand.objects.get(name='Test Brand Two')
        self.assertEqual(created_brand.alias, 'Test Brand 2')
        self.assertEqual(created_brand.key, 'TB2')
        self.assertEqual(list(created_brand.partners.all()), [self.partner])

    def test_brand_form_valid(self):
        form_data = {
            'id': 2,
            'name': 'Test Brand',
            'alias': 'Test Brand 2',
            'key': 'TB2',
            'partners': [self.partner.id]
        }
        form = BrandForm(data=form_data)
        self.assertTrue(form.is_valid())


class BrandsDetailsViewTest(TestCase):
    def setUp(self):

        self.username = 'admin'
        self.password = 'adminpassword'

        user = User.objects.create_superuser(
            username='admin',
            password='adminpassword',
            email='admin@example.com'
        )
        self.user = user

        self.client = Client()
        self.client.login(username=self.username, password=self.password)

        # Create a test partner for the view
        self.partner = Partner.objects.create(
            id=1,
            name='Test Partner',
            key='TP1',
            domain_name='testpartner.com',
            date=make_aware(datetime.datetime.now()),
            feed=11
        )
        # Create a test brand for the view
        self.brand = Brand.objects.create(
            id=1,
            name='Test Brand One',
            alias='Test Brand 1',
            key='TB1',
            date=make_aware(datetime.datetime.now())
        )
        self.brand.partners.set([self.partner.id])

    @classmethod
    def tearDownClass(cls):
        Brand.objects.all().delete()
        Partner.objects.all().delete()

    def test_brand_details_view_url_exists_at_desired_location(self):
        response = self.client.get('/brands/1/')
        self.assertEqual(response.status_code, 200)

    def test_brand_details_view_accessible_by_name(self):
        response = self.client.get(reverse('brand-detail', args=[self.brand.id]))
        self.assertEqual(response.status_code, 200)

    def test_brand_details_view_uses_correct_template(self):
        response = self.client.get(reverse('brand-detail', args=[self.brand.id]))
        self.assertTemplateUsed(response, 'brands/details.html')

    def test_brand_details_view_displays_correct_data(self):
        response = self.client.get(reverse('brand-detail', args=[self.brand.id]))
        self.assertContains(response, 'Test Brand One')
        self.assertContains(response, 'Test Brand 1')

    def test_brand_details_view_returns_404_for_invalid_brand_id(self):
        # Assuming there is no brand with ID 999
        response = self.client.get('/brands/999/')
        self.assertEqual(response.status_code, 404)

    def test_brand_details_view_context_contains_brand_object(self):
        response = self.client.get(reverse('brand-detail', args=[self.brand.id]))
        self.assertIn('brand', response.context)
        self.assertEqual(response.context['brand'], self.brand)


class BrandsUpdateViewTest(TestCase):
    def setUp(self):
        self.username = 'admin'
        self.password = 'adminpassword'

        user = User.objects.create_superuser(
            username='admin',
            password='adminpassword',
            email='admin@example.com'
        )
        self.user = user
        self.client = Client()
        self.client.login(username=self.username, password=self.password)

        # Create a test partner for the view
        self.partner = Partner.objects.create(
            id=1,
            name='Test Partner',
            key='TP1',
            domain_name='testpartner.com',
            date=make_aware(datetime.datetime.now()),
            feed=11
        )
        # Create a test brand for the view
        self.brand = Brand.objects.create(
            id=1,
            name='Test Brand One',
            alias='Test Brand 1',
            key='TB1',
            date=make_aware(datetime.datetime.now())
        )
        self.brand.partners.set([self.partner.id])

    @classmethod
    def tearDownClass(cls):
        Brand.objects.all().delete()
        Partner.objects.all().delete()

    def test_brand_update_view_url_exists_at_desired_location(self):
        response = self.client.get(f'/brands/{self.brand.id}/update/')
        self.assertEqual(response.status_code, 200)

    def test_brand_update_view_accessible_by_name(self):
        response = self.client.get(reverse('brand_update', args=[self.brand.id]))
        self.assertEqual(response.status_code, 200)

    def test_brand_update_view_uses_correct_template(self):
        response = self.client.get(reverse('brand_update', args=[self.brand.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'brands/update-brand.html')

    def test_brand_update_view_updates_brand(self):
        # Create a test brand for the view
        brand2 = Brand.objects.create(
            id=2,
            name='Test Brand Two',
            alias='Test Brand 2',
            key='TB2',
            date=make_aware(datetime.datetime.now())
        )
        brand2.partners.set([1])
        data = {
            'name': 'Updated Brand',
            'alias': 'updated_key',
            'key': 'UB',
            'partners': [1]
        }
        response = self.client.post(f'/brands/{brand2.id}/update/', data)
        # 302 indicates a successful redirect after form submission
        self.assertEqual(response.status_code, 302)

        # Check if the brand is updated in the database
        updated_brand = Brand.objects.get(id=brand2.id)
        self.assertEqual(updated_brand.name, 'Updated Brand')
        self.assertEqual(updated_brand.alias, 'updated_key')
        self.assertEqual(updated_brand.key, 'UB')
