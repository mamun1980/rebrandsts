from django.test import TestCase
from django.urls import reverse

from apps.partners.models import Partner
from apps.amenities.models import PartnerAmenityType, AmenityTypeCategory


class PartnerAmenityTypeTests(TestCase):
    def setUp(self):
        self.partner1 = Partner.objects.create(id=1, name='Booking', key='BC')
        self.partner2 = Partner.objects.create(id=2, name='Vrbo', key='VRBO')
        self.partner_type1 = PartnerAmenityType.objects.create(name='pool', partner=self.partner1)

    @classmethod
    def tearDownClass(cls):
        Partner.objects.all().delete()
        PartnerAmenityType.objects.all().delete()

    def test_add_partneramenitytype_successfully(self):
        partner_type = PartnerAmenityType(name='internet', partner=self.partner1)
        partner_type.save()

        # get partneramenitytype by specific id for verify
        data = PartnerAmenityType.objects.get(id=partner_type.id)
        self.assertEqual(data.name, 'internet')
        self.assertEqual(data.partner.name, 'Booking')

    def test_partneramenitytype_get_absolute_url(self):
        expected_url = reverse('partner-amenity-type-detail', args=[str(self.partner_type1.id)])
        actual_url = self.partner_type1.get_absolute_url()
        self.assertEqual(actual_url, expected_url)

    def test_update_partneramenitytype_successfully(self):
        # get partneramenitytype by specific id for update
        get_data = PartnerAmenityType.objects.get(id=self.partner_type1.id)
        get_data.partner = self.partner2
        get_data.save()

        data = PartnerAmenityType.objects.get(id=self.partner_type1.id)
        self.assertEqual(data.name, 'pool')
        self.assertEqual(data.partner.name, 'Vrbo')

    def test_delete_partneramenitytype_successfully(self):
        # get partneramenitytype by specific id for delete
        get_data = PartnerAmenityType.objects.get(id=self.partner_type1.id)
        get_data.delete()

        # Check if the PartnerAmenityType object was deleted from the database
        with self.assertRaises(PartnerAmenityType.DoesNotExist):
            PartnerAmenityType.objects.get(id=self.partner_type1.id)


class AmenityTypeCategoryTests(TestCase):
    def setUp(self):
        self.partner1 = Partner.objects.create(id=1, name='Booking', key='BC')
        self.partner2 = Partner.objects.create(id=2, name='Vrbo', key='VRBO')
        self.partner_type = PartnerAmenityType.objects.create(name='internet', partner=self.partner1)
        self.partner_type1 = PartnerAmenityType.objects.create(name='pool', partner=self.partner1)
        self.amenity = AmenityTypeCategory(name='internet')
        self.amenity.save()
        self.amenity.partner_amenity_type.set([self.partner_type.id])

    @classmethod
    def tearDownClass(cls):
        Partner.objects.all().delete()
        PartnerAmenityType.objects.all().delete()
        AmenityTypeCategory.objects.all().delete()

    def test_add_amenitytypecategory_successfully(self):
        amenity = AmenityTypeCategory(name='pool')
        amenity.save()
        amenity.partner_amenity_type.set([self.partner_type1.id])

        # get amenitytypecategory by specific id for verify
        data = AmenityTypeCategory.objects.get(id=amenity.id)
        self.assertEqual(data.name, 'pool')
        self.assertEqual(data.partner_amenity_type.all()[0].name, 'pool')

    def test_amenitytypecategory_get_absolute_url(self):
        expected_url = reverse('amenity-type-detail', args=[str(self.amenity.id)])
        actual_url = self.amenity.get_absolute_url()
        self.assertEqual(actual_url, expected_url)

    def test_update_amenitytypecategory_successfully(self):
        # get amenitytypecategory by specific id for update
        data = AmenityTypeCategory.objects.get(id=self.amenity.id)
        data.name = 'kitchen'
        data.save()

        get_data = AmenityTypeCategory.objects.get(id=self.amenity.id)
        self.assertEqual(get_data.name, 'kitchen')

    def test_delete_amenitytypecategory_successfully(self):
        # get amenitytypecategory by specific id for delete
        get_data = AmenityTypeCategory.objects.get(id=self.amenity.id)
        get_data.delete()

        # Check if the amenitytypecategory object was deleted from the database
        with self.assertRaises(AmenityTypeCategory.DoesNotExist):
            AmenityTypeCategory.objects.get(id=self.amenity.id)
