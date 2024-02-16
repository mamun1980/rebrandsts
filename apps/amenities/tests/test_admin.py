from django.test import TestCase, Client
from django.contrib.admin.sites import AdminSite
from django.urls import reverse

from django.contrib.auth.models import User
from apps.partners.models import Partner
from apps.amenities.models import PartnerAmenityType, AmenityTypeCategory


class SetUpClass(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.username = 'admin'
        cls.password = 'adminpassword'
        user = User.objects.create_superuser(
            username='admin',
            password='adminpassword',
            email='admin@example.com'
        )
        cls.user = user

    def setUp(self):
        self.client = Client()
        self.client.login(username=self.username, password=self.password)
        self.site = AdminSite()

    @classmethod
    def tearDownClass(cls):
        User.objects.all().delete()


class LeftTravelAmenityTypeAdminTestCase(SetUpClass):

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        Partner.objects.all().delete()
        PartnerAmenityType.objects.all().delete()
        AmenityTypeCategory.objects.all().delete()

    def setUp(self):
        super().setUp()
        self.partner1 = Partner.objects.create(id=1, name='Booking', key='BC')
        self.partner2 = Partner.objects.create(id=2, name='Vrbo', key='VRBO')
        self.partner_type = PartnerAmenityType.objects.create(name='internet', partner=self.partner1)
        self.amenity = AmenityTypeCategory(name='internet')
        self.amenity.save()
        self.amenity.partner_amenity_type.set([self.partner_type.id])

    def test_admin_amenitytypecategory_url_accessible(self):
        url = reverse('admin:amenities_amenitytypecategory_changelist')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name[0], 'admin/amenities/amenitytypecategory/change_list.html')

    def test_admin_amenitytypecategory_add_page_url_accessible(self):
        add_url = reverse('admin:amenities_amenitytypecategory_add')

        response = self.client.get(add_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Add LeftTravel Amenity Type')

    def test_admin_amenitytypecategory_add(self):
        add_url = reverse('admin:amenities_amenitytypecategory_add')
        redirect_url = reverse('admin:amenities_amenitytypecategory_changelist')

        partner_type = PartnerAmenityType.objects.create(name='pool', partner=self.partner2)
        param = {
            "name": 'pool',
            "partner_amenity_type": [partner_type.id]
        }
        response = self.client.post(add_url, param)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, redirect_url)

    def test_admin_amenitytypecategory_update(self):
        change_url = reverse('admin:amenities_amenitytypecategory_change', args=[self.amenity.id])
        redirect_url = reverse('admin:amenities_amenitytypecategory_changelist')

        partner_type = PartnerAmenityType.objects.create(name='internet', partner=self.partner2)
        param = {
            'id': self.amenity.id,
            'name': 'internet',
            "partner_amenity_type": [partner_type.id]
        }
        response = self.client.post(change_url, param)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, redirect_url)

    def test_admin_amenitytypecategory_delete(self):
        # Get the URL for deleting the AmenityTypeCategory instance
        delete_url = reverse('admin:amenities_amenitytypecategory_delete', args=[self.amenity.id])
        redirect_url = reverse('admin:amenities_amenitytypecategory_changelist')

        # Send a POST request to delete the AmenityTypeCategory instance
        response = self.client.post(delete_url, data={'post': 'yes'})

        # Check that the response status code is 302, indicating a successful delete and redirect
        self.assertEqual(response.status_code, 302)

        # Check the redirected URL or the list view after deletion
        self.assertRedirects(response, redirect_url)

        # Check if the AmenityTypeCategory object was deleted from the database
        with self.assertRaises(AmenityTypeCategory.DoesNotExist):
            AmenityTypeCategory.objects.get(id=self.amenity.id)


class PartnerAmenityTypeAdminTestCase(SetUpClass):

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        Partner.objects.all().delete()
        PartnerAmenityType.objects.all().delete()

    def setUp(self):
        super().setUp()
        self.partner1 = Partner.objects.create(id=1, name='Booking', key='BC')
        self.partner2 = Partner.objects.create(id=2, name='Vrbo', key='VRBO')
        self.partner_type = PartnerAmenityType.objects.create(name='internet', partner=self.partner1)

    def test_admin_partneramenitytype_url_accessible(self):
        url = reverse('admin:amenities_partneramenitytype_changelist')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name[0], 'admin/amenities/partneramenitytype/change_list.html')

    def test_admin_partneramenitytype_add_page_url_accessible(self):
        add_url = reverse('admin:amenities_partneramenitytype_add')

        response = self.client.get(add_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Add partner amenity type')

    def test_admin_partneramenitytype_add(self):
        add_url = reverse('admin:amenities_partneramenitytype_add')
        redirect_url = reverse('admin:amenities_partneramenitytype_changelist')

        param = {
            "name": 'pool',
            "partner": self.partner2.id
        }
        response = self.client.post(add_url, param)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, redirect_url)

    def test_admin_partneramenitytype_update(self):
        change_url = reverse('admin:amenities_partneramenitytype_change', args=[self.partner_type.id])
        redirect_url = reverse('admin:amenities_partneramenitytype_changelist')

        param = {
            'name': 'internet',
            "partner": self.partner2.id
        }
        response = self.client.post(change_url, param)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, redirect_url)

    def test_admin_partneramenitytype_delete(self):
        # Get the URL for deleting the PartnerAmenityType instance
        delete_url = reverse('admin:amenities_partneramenitytype_delete', args=[self.partner_type.id])
        redirect_url = reverse('admin:amenities_partneramenitytype_changelist')

        # Send a POST request to delete the PartnerAmenityType instance
        response = self.client.post(delete_url, data={'post': 'yes'})

        # Check that the response status code is 302, indicating a successful delete and redirect
        self.assertEqual(response.status_code, 302)

        # Check the redirected URL or the list view after deletion
        self.assertRedirects(response, redirect_url)

        # Check if the PartnerAmenityType object was deleted from the database
        with self.assertRaises(PartnerAmenityType.DoesNotExist):
            PartnerAmenityType.objects.get(id=self.partner_type.id)


