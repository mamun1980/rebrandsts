from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse


class AuthenticationTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        self.username = 'adminuser'
        self.password = 'adminpassword'
        self.useremail = 'admin@example.com'
        self.user = User.objects.create_superuser(
            username=self.username,
            password=self.password,
            email=self.useremail
        )

    def teardown(self):
        pass

    def test_user_created(self):
       user = User.objects.filter(username=self.username)
       self.assertTrue(user.exists())

    def test_user_email(self):
        user = User.objects.get(username=self.username)
        self.assertEquals(user.email, self.useremail)

    def test_admin_login(self):
        # Log in to the admin site
        self.client.login(username=self.username, password=self.password)

        # Access the admin index page
        response = self.client.get(reverse('admin:index'))

        # Check if the response indicates successful login
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'STS Admin Site')

    def test_admin_logout(self):
        # Log in to the admin site
        self.client.login(username=self.username, password=self.password)

        # Log out from the admin site
        response = self.client.get(reverse('admin:logout'), follow=True)

        # Check if the response indicates successful logout (redirects to login page)
        self.assertEqual(response.status_code, 200)