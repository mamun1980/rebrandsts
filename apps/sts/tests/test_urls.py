from django.test import TestCase
from django.urls import reverse


class STSURLTests(TestCase):

    def test_home_url_resolves(self):
        url = reverse('sts:confirm_bulk_update')
        self.assertEqual(url, '/admin/confirm-bulk-update/')