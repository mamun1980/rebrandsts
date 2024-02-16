# from django.test import TestCase
# from django.urls import reverse
# from apps.sts.models import BrandLocationDefinedSetsRatio, RatioSet
# from apps.sts.views import confirm_bulk_update, perform_bulk_update
#
#
# class BulkUpdateTestCase(TestCase):
#
#     def test_confirm_bulk_update(self):
#         # Test confirm_bulk_update view
#         url = reverse('confirm_bulk_update')
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, 200)
#
#     def test_perform_bulk_update(self):
#         # Test perform_bulk_update view
#         url = reverse('perform_bulk_update')
#         data = {
#             'action': 'confirm_action',
#             'ratio_set_title': 'Test Ratio Set',
#             'partner_ratios': ['50'],
#             'partner_ids': ['1'],
#             'location': '1',
#             'device': '1',
#             'property_group': '1',
#             'search_location': '1',
#             'selected_objects': [str(self.selected_object.id)],
#         }
#
#         response = self.client.post(url, data)
#         self.assertEqual(response.status_code, 302)  # Redirect after successful post
#
#         # Check if the objects were updated as expected
#         self.selected_object.refresh_from_db()
#         self.assertEqual(self.selected_object.ratio_set.title, 'Test Ratio Set')
#
#         # Add more assertions as needed
#
