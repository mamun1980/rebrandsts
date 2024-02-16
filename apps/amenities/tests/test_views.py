import json
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

from apps.partners.models import Partner
from apps.amenities.models import PartnerAmenityType, AmenityTypeCategory


class CommonTestCase(TestCase):
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
        User.objects.all().delete()


class AmenityTypeListViewTest(CommonTestCase):
    amenity_list = ["Air Conditioner", "Pet Friendly", "Pool", "TV", "View", "Wheelchair"]
    url = reverse('amenity-type-list')

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        Partner.objects.all().delete()
        PartnerAmenityType.objects.all().delete()
        AmenityTypeCategory.objects.all().delete()

    def setUp(self):
        super().setUp()
        partner = Partner.objects.create(id=1, name='Booking', key='BC')
        for amenity in self.amenity_list:
            partner_type = PartnerAmenityType.objects.create(name=amenity, partner=partner)
            amenity = AmenityTypeCategory.objects.create(name=amenity)
            amenity.partner_amenity_type.add(partner_type)

    def test_amenity_type_list_view_url_exists(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(self.url)

        self.assertTemplateUsed(response, 'generic_views/list_view.html')
        self.assertEqual(len(response.context_data['object_list']), len(self.amenity_list))

    def test_check_view_pagination(self):
        response = self.client.get(self.url)

        self.assertEqual(response.context_data['is_paginated'], False)

    def test_check_views_context_data(self):
        response = self.client.get(self.url)

        self.assertEqual(response.context_data['list_title'], 'LeftTravel Amenity Type List')
        self.assertEqual(response.context_data['button_urls'][0], 'add-amenity-type')


class AmenityTypeCreateViewTest(CommonTestCase):
    url = reverse('add-amenity-type')

    def setUp(self):
        super().setUp()
        self.partner = Partner.objects.create(id=1, name='Booking', key='BC')
        self.partner_type = PartnerAmenityType.objects.create(name='Air Conditioner', partner=self.partner)
        self.partner_type2 = PartnerAmenityType.objects.create(name='Pet Friendly', partner=self.partner)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        Partner.objects.all().delete()
        PartnerAmenityType.objects.all().delete()
        AmenityTypeCategory.objects.all().delete()

    def test_amenity_type_create_view_url_is_ok(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'generic_views/add_item_view.html')

    def test_check_views_context_data(self):
        response = self.client.get(self.url)

        self.assertEqual(response.context_data['title'], 'LeftTravel Amenity Type CreateView')
        self.assertListEqual(list(response.context_data.get('form').fields), ['name', 'partner_amenity_type'])

    def test_add_leftTravel_amenity_type(self):
        data = {
            'name': 'Air Conditioner',
            'partner_amenity_type': [self.partner_type.id, self.partner_type2.id]
        }
        response = self.client.post(self.url, data)

        # get AmenityTypeCategory data from db to verify
        get_data = AmenityTypeCategory.objects.all()
        partner_amenity_type_data = get_data[0].partner_amenity_type.all()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(get_data), 1)
        self.assertEqual(get_data[0].name, 'Air Conditioner')
        self.assertEqual(len(partner_amenity_type_data), 2)


class AmenityTypeDetailViewTest(CommonTestCase):
    def setUp(self):
        super().setUp()
        self.partner = Partner.objects.create(id=1, name='Booking', key='BC')
        self.partner_type = PartnerAmenityType.objects.create(name='Air Conditioner', partner=self.partner)
        self.partner_type2 = PartnerAmenityType.objects.create(name='Pet Friendly', partner=self.partner)
        self.amenity = AmenityTypeCategory(name='Air Conditioner')
        self.amenity.save()
        self.amenity.partner_amenity_type.set([self.partner_type.id])

        self.url = reverse('amenity-type-detail', args=[self.amenity.id])

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        Partner.objects.all().delete()
        PartnerAmenityType.objects.all().delete()
        AmenityTypeCategory.objects.all().delete()

    def test_amenity_type_create_view_url_is_ok(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'generic_views/details_view.html')

    def test_check_views_context_data(self):
        response = self.client.get(self.url)

        self.assertEqual(response.context_data['title'], 'LeftTravel Amenity Type DetailView')
        self.assertEqual(response.context_data['object'].name, 'Air Conditioner')


class AmenityTypeUpdateViewTest(CommonTestCase):
    def setUp(self):
        super().setUp()
        self.partner = Partner.objects.create(id=1, name='Booking', key='BC')
        self.partner_type = PartnerAmenityType.objects.create(name='Air Conditioner', partner=self.partner)
        self.partner_type2 = PartnerAmenityType.objects.create(name='Pet Friendly', partner=self.partner)
        self.amenity = AmenityTypeCategory(name='Air Conditioner')
        self.amenity.save()
        self.amenity.partner_amenity_type.set([self.partner_type.id])

        self.url = reverse('amenity-type-update', args=[self.amenity.id])

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        Partner.objects.all().delete()
        PartnerAmenityType.objects.all().delete()
        AmenityTypeCategory.objects.all().delete()

    def test_amenity_type_update_view_url_is_ok(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'generic_views/update_form.html')

    def test_check_views_context_data(self):
        response = self.client.get(self.url)

        self.assertEqual(response.context_data['title'], 'LeftTravel Amenity Type UpdateView')
        self.assertEqual(response.context_data['object'].name, 'Air Conditioner')
        self.assertListEqual(list(response.context_data.get('form').fields), ['name', 'partner_amenity_type'])

    def test_update_leftTravel_amenity_type(self):
        data = {
            'name': 'Pool',
            'partner_amenity_type': [self.partner_type.id, self.partner_type2.id]
        }
        response = self.client.post(self.url, data)
        # get AmenityTypeCategory data from db to verify
        get_data = AmenityTypeCategory.objects.all()
        partner_amenity_type_data = get_data[0].partner_amenity_type.all()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(get_data), 1)
        self.assertEqual(get_data[0].name, 'Pool')
        self.assertEqual(len(partner_amenity_type_data), 2)


class AmenityTypeDeleteViewTest(CommonTestCase):
    def setUp(self):
        super().setUp()
        self.partner = Partner.objects.create(id=1, name='Booking', key='BC')
        self.partner_type = PartnerAmenityType.objects.create(name='Air Conditioner', partner=self.partner)
        self.partner_type2 = PartnerAmenityType.objects.create(name='Pet Friendly', partner=self.partner)
        self.amenity = AmenityTypeCategory(name='Air Conditioner')
        self.amenity.save()
        self.amenity.partner_amenity_type.set([self.partner_type.id])

        self.url = reverse('amenity-type-delete', args=[self.amenity.id])

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        Partner.objects.all().delete()
        PartnerAmenityType.objects.all().delete()
        AmenityTypeCategory.objects.all().delete()

    def test_amenity_type_delete_view_url_is_ok(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'amenities/amenitytypecategory_confirm_delete.html')

    def test_check_views_context_data(self):
        response = self.client.get(self.url)
        self.assertContains(response, 'Confirm Amenity Type Delete')
        self.assertEqual(response.context_data['object'].name, 'Air Conditioner')

    def test_delete_leftTravel_amenity_type(self):
        redirect_url = reverse('amenity-type-list')

        get_data = AmenityTypeCategory.objects.get(id=self.amenity.id)

        response = self.client.post(self.url)
        # Check that the response status code is 302, indicating a successful delete and redirect
        self.assertEqual(response.status_code, 302)

        # Check the redirected URL or the list view after deletion
        self.assertRedirects(response, redirect_url)

        # Check if the AmenityTypeCategory object was deleted from the database
        with self.assertRaises(AmenityTypeCategory.DoesNotExist):
            AmenityTypeCategory.objects.get(id=self.amenity.id)


class PartnerAmenityTypeListViewTest(CommonTestCase):
    amenity_list = ["Air Conditioner", "Pet Friendly", "Pool", "TV", "View", "Wheelchair"]

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        Partner.objects.all().delete()
        PartnerAmenityType.objects.all().delete()
        AmenityTypeCategory.objects.all().delete()

    def setUp(self):
        super().setUp()
        self.url = reverse('partner-amenity-type-list')
        self.partner = Partner.objects.create(id=1, name='Booking', key='BC')
        for amenity in self.amenity_list:
            PartnerAmenityType.objects.create(name=amenity, partner=self.partner)

    def test_partner_amenity_type_list_view_url_exists(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(self.url)

        self.assertTemplateUsed(response, 'generic_views/list_view.html')
        self.assertEqual(len(response.context_data['object_list']), len(self.amenity_list))

    def test_check_view_pagination(self):
        response = self.client.get(self.url)

        self.assertEqual(response.context_data['is_paginated'], False)

    def test_check_views_context_data(self):
        response = self.client.get(self.url)

        self.assertEqual(response.context_data['list_title'], 'Partner Amenity Type List')
        self.assertEqual(response.context_data['button_urls'][0], 'add-partner-amenity-type')


class PartnerAmenityCreateViewTest(CommonTestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse('add-partner-amenity-type')
        self.partner = Partner.objects.create(id=1, name='Booking', key='BC')
        self.partner_type = PartnerAmenityType.objects.create(name='Air Conditioner', partner=self.partner)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        Partner.objects.all().delete()
        PartnerAmenityType.objects.all().delete()

    def test_partner_amenity_type_create_view_url_is_ok(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'generic_views/add_item_view.html')

    def test_check_views_context_data(self):
        response = self.client.get(self.url)

        self.assertEqual(response.context_data['title'], 'Partner Amenity Type CreateView')
        self.assertListEqual(list(response.context_data.get('form').fields), ['name', 'partner'])

    def test_add_partner_amenity_type_type(self):
        data = {
            'name': 'Pet Friendly',
            'partner': self.partner.id
        }
        response = self.client.post(self.url, data)

        # get PartnerAmenityType data from db to verify
        get_data = PartnerAmenityType.objects.all()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(get_data), 2)
        self.assertEqual(get_data[self.partner.id].name, 'Pet Friendly')


class PartnerAmenityDetailViewTest(CommonTestCase):
    def setUp(self):
        super().setUp()
        self.partner = Partner.objects.create(id=1, name='Booking', key='BC')
        self.partner_type = PartnerAmenityType.objects.create(name='Air Conditioner', partner=self.partner)
        self.url = reverse('partner-amenity-type-detail', args=[self.partner_type.id])

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        Partner.objects.all().delete()
        PartnerAmenityType.objects.all().delete()

    def test_partner_amenity_type_create_view_url_is_ok(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'generic_views/details_view.html')

    def test_check_views_context_data(self):
        response = self.client.get(self.url)

        self.assertEqual(response.context_data['title'], 'Partner Amenity Type DetailView')
        self.assertEqual(response.context_data['object'].name, 'Air Conditioner')


class PartnerAmenityUpdateViewTest(CommonTestCase):
    def setUp(self):
        super().setUp()
        self.partner = Partner.objects.create(id=1, name='Booking', key='BC')
        self.partner_type = PartnerAmenityType.objects.create(name='Air Conditioner', partner=self.partner)
        self.url = reverse('partner-amenity-type-update', args=[self.partner_type.id])

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        Partner.objects.all().delete()
        PartnerAmenityType.objects.all().delete()

    def test_partner_amenity_type_update_view_url_is_ok(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'generic_views/update_form.html')

    def test_check_views_context_data(self):
        response = self.client.get(self.url)

        self.assertEqual(response.context_data['title'], 'Partner Amenity Type UpdateView')
        self.assertEqual(response.context_data['object'].name, 'Air Conditioner')
        self.assertListEqual(list(response.context_data.get('form').fields), ['name', 'partner'])

    def test_update_partner_amenity_type(self):
        data = {
            'name': 'Pet Friendly',
            'partner': self.partner.id
        }
        response = self.client.post(self.url, data)

        # get PartnerAmenityType data from db to verify
        get_data = PartnerAmenityType.objects.all()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(get_data), 1)
        self.assertEqual(get_data[0].name, 'Pet Friendly')


class PartnerAmenityDeleteViewTest(CommonTestCase):
    def setUp(self):
        super().setUp()
        self.partner = Partner.objects.create(id=1, name='Booking', key='BC')
        self.partner_type = PartnerAmenityType.objects.create(name='Air Conditioner', partner=self.partner)
        self.url = reverse('partner-amenity-type-delete', args=[self.partner_type.id])

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        Partner.objects.all().delete()
        PartnerAmenityType.objects.all().delete()

    def test_partner_amenity_type_delete_view_url_is_ok(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(self.url)

        self.assertTemplateUsed(response, 'amenities/partneramenitytype_confirm_delete.html')

    def test_check_views_context_data(self):
        response = self.client.get(self.url)
        self.assertContains(response, 'Confirm Partner Amenity Type Delete')
        self.assertEqual(response.context_data['object'].name, 'Air Conditioner')

    def test_delete_partner_amenity_type(self):
        redirect_url = reverse('partner-amenity-type-list')

        response = self.client.post(self.url)
        # Check that the response status code is 302, indicating a successful delete and redirect
        self.assertEqual(response.status_code, 302)

        # Check the redirected URL or the list view after deletion
        self.assertRedirects(response, redirect_url)

        # Check if the PartnerAmenityType object was deleted from the database
        with self.assertRaises(PartnerAmenityType.DoesNotExist):
            PartnerAmenityType.objects.get(id=self.partner_type.id)


class AmenityTypeMappingViewTest(CommonTestCase):
    def setUp(self):
        super().setUp()
        self.partner = Partner.objects.create(id=1, name='Booking', key='BC')
        self.partner_type = PartnerAmenityType.objects.create(name='Air Conditioner', partner=self.partner)
        self.partner_type2 = PartnerAmenityType.objects.create(name='Pet Friendly', partner=self.partner)
        self.amenity = AmenityTypeCategory(name='Air Conditioner')
        self.amenity.save()
        self.amenity.partner_amenity_type.set([self.partner_type.id])

        self.url = reverse('amenity-type-mapping')

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        Partner.objects.all().delete()
        PartnerAmenityType.objects.all().delete()
        AmenityTypeCategory.objects.all().delete()

    def test_amenity_type_mapping_view_url_is_ok(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(self.url)

        self.assertTemplateUsed(response, 'amenities/drag_and_drop_amenity_mapping.html')

    def test_check_partner_amenity_type_mapping_post_request_for_partner_amenity(self):
        data = {
            'lefttravel-type-booking-com': [],
            'booking-com-partner-amenity-type': ['{"%d":["%d"]}' % (self.amenity.id, self.partner_type.id)]
        }
        response = self.client.post(self.url, data={'message': json.dumps(data)})

        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(json.loads(response.content), {'message': 'Data received and processed successfully'})

    def test_check_partner_amenity_type_mapping_post_request_for_lefttravel_amenity(self):
        data = {
            'lefttravel-type-booking-com': [f"{self.partner_type.id}"],
            'booking-com-partner-amenity-type': []
        }
        response = self.client.post(self.url, data={'message': json.dumps(data)})

        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(json.loads(response.content), {'message': 'Data received and processed successfully'})

    def test_check_partner_amenity_type_mapping_post_without_amenity(self):
        data = {
            'lefttravel-type-booking-com': [f"{self.partner_type.id}"],
            'booking-com-partner-amenity-type': []
        }
        response = self.client.post(self.url, data=data)

        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(json.loads(response.content), {'error': 'This is not a valid request.'})

    def test_check_partner_amenity_type_mapping_post_excption(self):
        data = {
            'lefttravel-type-booking-com': [],
            'booking-com-partner-amenity-type': ['{"1":"None"}']
        }
        response = self.client.post(self.url, data={'message': json.dumps(data)})

        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(json.loads(response.content), {'message': 'Data received and processed successfully'})
