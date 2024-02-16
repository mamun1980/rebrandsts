from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.test import RequestFactory
from django.contrib.admin.sites import AdminSite
from apps.property.models import *
from apps.sts.admin import *
from apps.sts.models import *


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

    def setUp(self):
        self.client = Client()
        self.client.login(username=self.username, password=self.password)
        self.site = AdminSite()


class DeviceAdminTestCase(SetUpClass):

    @classmethod
    def tearDownClass(cls):
        User.objects.all().delete()
        Device.objects.all().delete()

    def setUp(self):
        super().setUp()
        self.model_admin = DeviceAdmin(Device, self.site)

    def test_save_model_method_in_device_admin(self):
        obj = Device(type='Test Object', sort_order=1)
        request = self.request_factory.post('/admin/sts/device/add/')
        request.user = self.user

        # Call the save_model method
        self.model_admin.save_model(request, obj, None, None)

        # Retrieve the object from the database to check if it was saved
        saved_obj = Device.objects.get(pk=obj.pk)

        # Assert that the object was saved correctly
        self.assertEqual(saved_obj.type, 'Test Object')

    def test_we_can_add_device(self):
        param = {
            "type": 'Mobile',
            "sort_order": 1
        }
        response = self.client.post('/admin/sts/device/add/', param, content_type='application/x-www-form-urlencoded')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/change_form.html')

    def test_admin_url_device_list_page_accessible(self):
        response = self.client.get('/admin/sts/device/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Select device to change')

    def test_admin_url_device_add_page_accessible(self):
        response = self.client.get('/admin/sts/device/add/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Add device')


class LocationAdminTestCase(SetUpClass):
    @classmethod
    def tearDownClass(cls):
        User.objects.all().delete()
        Location.objects.all().delete()

    def setUp(self):
        super().setUp()
        self.model_admin = LocationAdmin(Location, self.site)
        # Create a Location instance for testing
        self.location = Location.objects.create(
            id=1,
            location_type='country',
            country_code='BD',
            country='Bangladesh'
        )

    def test_save_model_method_in_location_admin(self):
        obj = Location(location_type='country', country_code='CA', country='Canada')
        request = self.request_factory.post('/admin/sts/location/add/')
        request.user = self.user

        # Call the save_model method
        self.model_admin.save_model(request, obj, None, None)

        # Retrieve the object from the database to check if it was saved
        saved_obj = Location.objects.get(pk=obj.pk)

        # Assert that the object was saved correctly
        self.assertEqual(saved_obj.location_type, 'country')
        self.assertEqual(saved_obj.country_code, 'CA')
        self.assertEqual(saved_obj.country, 'Canada')

    def test_admin_url_location_list_page_accessible(self):
        response = self.client.get('/admin/sts/location/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Select location to change')

    def test_admin_url_location_add_page_accessible(self):
        response = self.client.get('/admin/sts/location/add/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Add location')

    def test_we_can_add_location(self):
        add_url = reverse('admin:sts_location_add')
        expected_redirect_url = reverse('admin:sts_location_changelist')
        param = {
            "location_type": 'country',
            "country_code": 'US',
            "country": 'United States'
        }
        response = self.client.post(add_url, param)
        # After added redirect to changelist page
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, expected_redirect_url)

    def test_location_required_fields(self):
        location_data = {
            "id": 4,
            "location_type": 'country',
        }
        # Try to create a new location without required fields
        response = self.client.post(
            reverse('admin:sts_location_add'),
            location_data,
            content_type='application/x-www-form-urlencoded'
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This field is required.", count=2)
        self.assertFalse(Location.objects.filter(id=4).exists())

    def test_location_update(self):
        # Update data for the Location instance
        updated_data = {
            "id": 1,
            "location_type": 'country',
            "country_code": 'BD',
            "country": 'Digital Bangladesh'
        }
        # Get the URL for updating the Location instance
        update_url = reverse('admin:sts_location_change', args=[self.location.id])
        redirect_url = reverse('admin:sts_location_changelist')

        # Send a POST request to update the Location instance
        response = self.client.post(update_url, updated_data)
        # Check that the response status code is 302, indicating a successful update and redirect
        self.assertEqual(response.status_code, 302)
        # Check the redirected URL
        self.assertEqual(response.url, redirect_url)

        # Check if the Location object was updated in the database
        updated_location = Location.objects.get(id=self.location.id)
        self.assertEqual(updated_location.country_code, 'BD')
        self.assertEqual(updated_location.country, 'Digital Bangladesh')

    def test_location_delete(self):
        # Get the URL for deleting the Location instance
        delete_url = reverse('admin:sts_location_delete', args=[self.location.id])
        expected_redirect_url = reverse('admin:sts_location_changelist')
        # Send a POST request to delete the Location instance
        response = self.client.post(
            delete_url,
            data={'post': 'yes'},
            content_type='application/x-www-form-urlencoded'
        )
        # Check that the response status code is 302, indicating a successful delete and redirect
        self.assertEqual(response.status_code, 302)

        # Check the redirected URL or the list view after deletion
        self.assertRedirects(response, expected_redirect_url)

        # Check if the Location object was deleted from the database
        with self.assertRaises(Location.DoesNotExist):
            deleted_location = Location.objects.get(id=self.location.id)


class SearchLocationAdminTestCase(SetUpClass):
    def setUp(self):
        super().setUp()
        self.model_admin = SearchLocationAdmin(SearchLocation, self.site)
        # Create a Location instance for testing
        location_type = LocationType.objects.create(name='country')
        self.location_type = location_type
        self.search_location = SearchLocation.objects.create(
            id=1,
            search_location='Italy',
            place_id='ChIJA9KNRIL-1BIRb15jJFz1LOI',
            sort_order=3,
            ep_location_id='86',
            type_level=1,
            location_type=location_type,
            slug='italy',
            location_level='1'
        )

    @classmethod
    def tearDownClass(cls):
        User.objects.all().delete()
        LocationType.objects.all().delete()
        SearchLocation.objects.all().delete()

    def test_admin_search_location_list_page_accessible(self):
        url = reverse('admin:sts_searchlocation_changelist')

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Select search location to change')

    def test_searchlocation_add_page_accessible(self):
        url = reverse('admin:sts_searchlocation_add')
        template_name = 'admin/sts/search_location/change_form.html'
        search_text = 'Add search location'

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, search_text)
        self.assertTemplateUsed(response, template_name)

    def test_admin_add_searchlocation(self):
        url = reverse('admin:sts_searchlocation_add')
        expected_redirect_url = reverse('admin:sts_searchlocation_changelist')
        data = {'search_location': 'Canada'}

        response = self.client.post(url, data)

        # Checked redirect to the checklist page
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, expected_redirect_url)

        # For Check if the SearchLocation object exists
        check_data = SearchLocation.objects.all()
        self.assertEqual(check_data.count(), 2)

    def test_admin_searchlocation_check_duplicate_insert(self):
        url = reverse('admin:sts_searchlocation_change', args=[self.search_location.id])
        data = {'search_location': 'Test Italy'}

        # Send a POST request to update the SearchLocation instance
        response = self.client.post(url, data)
        # Check that the response status code is 200, indicating not redirect
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Please correct the error below.', count=1)

    def test_admin_searchlocation_update(self):
        url = reverse('admin:sts_searchlocation_change', args=[self.search_location.id])
        data = {'search_location': 'Bangladesh'}
        redirect_url = reverse('admin:sts_searchlocation_changelist')

        # Send a POST request to update the SearchLocation instance
        response = self.client.post(url, data)

        # Check that the response status code is 302, indicating a successful update and redirect
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, redirect_url)

        # Verify the updated data in the database
        updated_search_location = SearchLocation.objects.get(id=self.search_location.id)
        self.assertEqual(updated_search_location.search_location, 'Bangladesh')

    def test_location_delete(self):
        # Get the URL for deleting the SearchLocation instance
        delete_url = reverse('admin:sts_searchlocation_delete', args=[self.search_location.id])
        redirect_url = reverse('admin:sts_searchlocation_changelist')
        # Send a POST request to delete the SearchLocation instance
        response = self.client.post(delete_url, data={'post': 'yes'})

        # Check that the response status code is 302, indicating a successful delete and redirect
        self.assertEqual(response.status_code, 302)

        # Check the redirected URL or the list view after deletion
        self.assertRedirects(response, redirect_url)

        # Check if the SearchLocation object was deleted from the database
        with self.assertRaises(SearchLocation.DoesNotExist):
            deleted_location = SearchLocation.objects.get(id=1)


class RatioLocationAdminTestCase(SetUpClass):
    @classmethod
    def tearDownClass(cls):
        User.objects.all().delete()
        RatioLocation.objects.all().delete()

    def setUp(self):
        super().setUp()
        self.model_admin = RatioLocationAdmin(RatioLocation, self.site)

    def test_save_model_method_in_ratio_location_admin(self):
        obj = RatioLocation(location_name='test location')
        request = self.request_factory.post('/admin/sts/ratiolocation/add/')
        request.user = self.user

        # Call the save_model method
        self.model_admin.save_model(request, obj, None, None)

        # Retrieve the object from the database to check if it was saved
        saved_obj = RatioLocation.objects.get(pk=obj.pk)

        # Assert that the object was saved correctly
        self.assertEqual(saved_obj.location_name, 'test location')

    def test_admin_url_ratio_location_list_page_accessible(self):
        response = self.client.get('/admin/sts/ratiolocation/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Select ratio location to change')

    def test_admin_url_ratio_location_add_page_accessible(self):
        response = self.client.get('/admin/sts/ratiolocation/add/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Add ratio location')

    def test_we_can_add_ratio_location(self):
        param = {
            "location_name": 'test_ratio_location'
        }
        response = self.client.post('/admin/sts/ratiolocation/add/', param, content_type='application/x-www-form-urlencoded')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/change_form.html')

    def test_admin_ratio_location_add(self):
        url = reverse('admin:sts_ratiolocation_add')
        redirect_url = reverse('admin:sts_ratiolocation_changelist')
        param = {'id': 1, "location_name": 'test_ratio_location'}
        response = self.client.post(url, param)

        # After added redirect to changelist page
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, redirect_url)


class RatioSetAdminTestCase(SetUpClass):
    @classmethod
    def tearDownClass(cls):
        User.objects.all().delete()
        RatioSet.objects.all().delete()
        RatioLocation.objects.all().delete()

    def setUp(self):
        super().setUp()
        self.model_admin = RatioSetAdmin(RatioSet, self.site)

        # create RationSet instance
        ratio_location = RatioLocation.objects.create(id=1, location_name='united states')
        ratio_set = RatioSet.objects.create(
            title='VRBO=60%, TC=40%',
            ratio_title='BC_60% VRBO_40%',
            ratio_location=ratio_location
        )

        self.ratio_location = ratio_location
        self.ratio_set = ratio_set

    def test_save_model_method_in_ratio_set_admin(self):
        obj = RatioSet(ratio_title='test ratio_title', ratio_location=self.ratio_location)
        url = reverse('admin:sts_ratioset_add')
        request = self.request_factory.post(url)
        request.user = self.user

        # Call the save_model method
        self.model_admin.save_model(request, obj, None, None)

        # Retrieve the object from the database to check if it was saved
        saved_obj = RatioSet.objects.get(pk=obj.pk)

        # Assert that the object was saved correctly
        self.assertEqual(saved_obj.ratio_title, 'test ratio_title')

    def test_admin_url_ratio_set_list_page_accessible(self):
        url = reverse('admin:sts_ratioset_changelist')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Select ratio set to change')

    def test_admin_url_ratio_set_add_page_accessible(self):
        url = reverse('admin:sts_ratioset_add')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Add ratio set')
        self.assertContains(response, 'Partner ratios')

    def test_we_can_add_ratio_set(self):
        url = reverse('admin:sts_ratioset_add')
        param = {
            "ratio_title": 'test_ratio_set',
            "ratio_location": self.ratio_location
        }
        response = self.client.post(url, param, content_type='application/x-www-form-urlencoded')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/change_form.html')

    # NOTE: Need work for add and update

    def test_check_ratio_set_admin_duplicate_insert(self):
        url = reverse('admin:sts_ratioset_change', args=[self.ratio_set.id])
        data = {
            "ratio_title": 'test_ratio_title',
            "ratio_location": self.ratio_location
        }
        # Send a POST request to update the SearchLocation instance
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Please correct the error below.')


class BrandLocationDefinedSetsRatioAdminTestCase(SetUpClass):
    @classmethod
    def tearDownClass(cls):
        User.objects.all().delete()
        RatioSet.objects.all().delete()
        PropertyGroup.objects.all().delete()
        Device.objects.all().delete()
        Location.objects.all().delete()
        Brand.objects.all().delete()
        SearchLocation.objects.all().delete()
        BrandLocationDefinedSetsRatio.objects.all().delete()

    def setUp(self):
        super().setUp()
        self.model_admin = BrandLocationDefinedSetsRatioAdmin(BrandLocationDefinedSetsRatio, self.site)

    def test_save_model_method_in_brandlocationdefinedsetsratio_admin(self):
        ratio_set = RatioSet.objects.create(title='test ratioset')
        property_group = PropertyGroup.objects.create(id=1,name='test property')
        device = Device.objects.create(id=1,type='Desktop')
        location = Location.objects.create(id=1,location_type='country', country='Canada', country_code='CA')
        brand = Brand.objects.create(id=1,name='test brand')
        search_location = SearchLocation.objects.create(id=1,search_location='Test')

        obj = BrandLocationDefinedSetsRatio(
            ratio_set=ratio_set,
            property_group=property_group,
            device=device,
            location=location,
            brand=brand,
            search_location=search_location
        )
        request = self.request_factory.post('/admin/sts/brandlocationdefinedsetsratio/add/')
        request.user = self.user

        # Call the save_model method
        self.model_admin.save_model(request, obj, None, None)

        # Retrieve the object from the database to check if it was saved
        saved_obj = BrandLocationDefinedSetsRatio.objects.get(pk=obj.pk)

        # Assert that the object was saved correctly
        self.assertEqual(saved_obj.id, obj.pk)

    def test_admin_url_brandlocationdefinedsetsratio_list_page_accessible(self):
        response = self.client.get('/admin/sts/brandlocationdefinedsetsratio/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Select Brand Location Ratio Set to change')

    def test_admin_url_brandlocationdefinedsetsratio_add_page_accessible(self):
        response = self.client.get('/admin/sts/brandlocationdefinedsetsratio/add/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Add Brand Location Ratio Set')
