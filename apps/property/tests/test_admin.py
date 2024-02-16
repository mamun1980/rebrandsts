from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from apps.property.models import PropertyGroup


class PropertyAdminTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.username = 'admin'
        cls.password = 'adminpassword'

        User.objects.create_superuser(
            username='admin',
            password='adminpassword',
            email='admin@example.com'
        )

    @classmethod
    def tearDownClass(cls):
        User.objects.all().delete()

    def setUp(self):
        self.client = Client()
        self.client.login(username=self.username, password=self.password)

    def test_admin_url_accessible(self):
        response = self.client.get(reverse('admin:index'))
        self.assertEqual(response.status_code, 200)

    def test_property_admin_list_page_access(self):
        response = self.client.get('/admin/property/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Property administration')

    def test_property_accomodation_type_admin_list_page_access(self):
        response = self.client.get('/admin/property/propertygroup/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Select Accommodation Type to change')
        # self.assertContains(response, 'Select Accommodation Type to change')


class PropertyGroupAdminTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.username = 'admin'
        cls.password = 'adminpassword'

        cls.user = User.objects.create_superuser(
            username='admin',
            password='adminpassword',
            email='admin@example.com'
        )

    @classmethod
    def tearDownClass(cls):
        User.objects.all().delete()

    def setUp(self):
        # Create a test user
        self.client = Client()
        self.client.login(username=self.username, password=self.password)

    def test_add_property_group_in_admin(self):
        # Log in the test user
        self.client.login(username='testuser', password='testpassword')

        # Get the URL for the "add" page of your model in the admin site
        add_url = reverse('admin:property_propertygroup_add')

        # Perform a GET request to access the add page
        response = self.client.get(add_url)
        # Check if the page is accessible (status code 200)
        self.assertEqual(response.status_code, 200)

        # Create a dictionary with data to add a new PropertyGroup instance
        data = {
            'id': 1,
            'name': 'New Property Group',
            # Add more fields as needed
        }

        # Perform a POST request to submit the form and add a new PropertyGroup instance
        response = self.client.post(add_url, data)

        # Check if the instance was successfully added (status code 302 for redirection)
        self.assertEqual(response.status_code, 302)

        # Check if the instance exists in the database
        self.assertTrue(PropertyGroup.objects.filter(name='New Property Group').exists())

    def test_edit_property_group_in_admin(self):
        # Create an instance of PropertyGroup for editing
        property_group_instance = PropertyGroup.objects.create(
            id=1,
            name='Edit Property Group',
            # Add more fields as needed
        )

        # Log in the test user
        self.client.login(username='testuser', password='testpassword')

        # Get the URL for the "change" page of your model in the admin site
        change_url = reverse('admin:property_propertygroup_change', args=[property_group_instance.id])

        # Perform a GET request to access the edit page
        response = self.client.get(change_url)

        # Check if the page is accessible (status code 200)
        self.assertEqual(response.status_code, 200)

        # Create a dictionary with data for editing the PropertyGroup instance
        updated_data = {
            'name': 'Updated Property Group',
            # Add more fields as needed
        }

        # Perform a POST request to submit the form and edit the PropertyGroup instance
        response = self.client.post(change_url, updated_data)

        # Check if the instance was successfully edited (status code 302 for redirection)
        self.assertEqual(response.status_code, 302)

        # Check if the instance has been updated in the database
        property_group_instance.refresh_from_db()
        self.assertEqual(property_group_instance.name, 'Updated Property Group')
        # Add more assertions for other fields as needed