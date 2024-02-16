from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
import datetime
from apps.partners.models import Partner, PartnerProvider


class PartnerAdminTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.username = 'admin'
        cls.password = 'adminpassword'

        User.objects.create_superuser(
            username='admin',
            password='adminpassword',
            email='admin@example.com'
        )

        Partner.objects.create(
            id=1,
            name='testpartnet1',
            key='TP1',
            domain_name='example1.com',
            feed=10,
            sort_order=1
        )

        Partner.objects.create(
            id=2,
            name='testpartnet2',
            key='TP2',
            domain_name='example2.com',
            feed=11,
            sort_order=2
        )


    @classmethod
    def tearDownClass(cls):
        Partner.objects.all().delete()
        User.objects.all().delete()

    def setUp(self):
        self.client = Client()
        self.client.login(username=self.username, password=self.password)

    def test_admin_url_accessible(self):
        response = self.client.get(reverse('admin:index'))
        self.assertEqual(response.status_code, 200)


    def test_partners_admin_list_page_access(self):
        response = self.client.get(reverse('admin:partners_partner_changelist'))
        self.assertEqual(response.status_code, 200)

    def test_partners_admin_list_page_content(self):
        response = self.client.get(reverse('admin:partners_partner_changelist'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'testpartnet1')
        self.assertContains(response, 'testpartnet2')
