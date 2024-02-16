import datetime

from django.test import TestCase
from apps.brands.models import Brand
from apps.partners.models import Partner
from apps.property.models import (
    PropertyGroup, PropertyCategory, PropertyType, PartnerPropertyType, PartnerPropertyMapping
)


class PropertyGroupModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        pg1 = PropertyGroup.objects.create(id=1, name='Hotels')
        pg2 = PropertyGroup.objects.create(id=2, name='Apartment')
        pg_list = [pg1, pg2]
        cls.pgs = pg_list

    @classmethod
    def tearDownClass(cls):
        PropertyGroup.objects.all().delete()

    def test_property_group_added_successfully(self):
        self.assertEqual(len(self.pgs), 2)
        self.assertEqual(self.pgs[0].name, 'Hotels')
        self.assertEqual(self.pgs[1].name, 'Apartment')


class PropertyCategoryModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        pg1 = PropertyGroup.objects.create(id=1, name='Hotels')
        pg2 = PropertyGroup.objects.create(id=2, name='Apartment')

        pc1 = PropertyCategory.objects.create(
            id=1,
            name='test_category_1',
            group=pg1
        )
        pc2 = PropertyCategory.objects.create(
            id=2,
            name='test_category_2',
            group=pg2
        )

        cls.pcs = [pc1, pc2]

    @classmethod
    def tearDownClass(cls):
        PropertyCategory.objects.all().delete()
        PropertyGroup.objects.all().delete()

    def test_model_content(self):
        self.assertEqual(len(self.pcs), 2)
        self.assertEqual(self.pcs[0].name, "test_category_1")
        self.assertEqual(self.pcs[0].group.name, "Hotels")
        self.assertEqual(self.pcs[1].name, "test_category_2")
        self.assertEqual(self.pcs[1].group.name, "Apartment")


class PropertyTypeModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        pg1 = PropertyGroup.objects.create(id=1, name='Hotels')
        rbo = Brand.objects.create(
            id=1,
            name="RentByOwner.com",
            alias="RENTBYOWNER",
            key="RBO",
            date="2020-02-20T11:22:28Z",
            sort_order=13,
            created_at="2023-08-04T05:50:03.921Z",
            updated_at="2023-08-04T05:50:03.921Z"
        )

        pt1 = PropertyType.objects.create(
            id=1,
            name="Bed_Breakfast",
            brand=rbo,
            brand_type="rentals",
            create_date="2023-08-04T08:50:46.288Z",
            update_date="2023-08-04T08:50:46.288Z",
        )
        pt1.accommodation_type.add(pg1)

        cls.property_type = pt1

    @classmethod
    def tearDownClass(cls):
        PropertyType.objects.all().delete()
        Brand.objects.all().delete()
        PropertyGroup.objects.all().delete()

    def test_model_content(self):
        self.assertEqual(self.property_type.name, 'Bed_Breakfast')
        self.assertEqual(self.property_type.brand.name, 'RentByOwner.com')
        self.assertEqual(self.property_type.accommodation_type.all()[0].name, 'Hotels')
        self.assertEqual(self.property_type.brand_type, 'rentals')


class PartnerPropertyTypeModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        partner = Partner.objects.create(
            id=1,
            name='Booking.com',
            key='BC',
            domain_name='booking.com',
            feed=11,
            sort_order=1
        )

        ppt1 = PartnerPropertyType.objects.create(
            id=189,
            name='Houseboat',
            partner=partner
        )
        ppt2 = PartnerPropertyType.objects.create(
            id=77,
            name='Motels',
            partner=partner
        )

        cls.ppt1 = ppt1
        cls.ppt2 = ppt2



    @classmethod
    def tearDownClass(cls):
        PartnerPropertyType.objects.all().delete()
        Partner.objects.all().delete()


    def test_model_content(self):
        self.assertEqual(self.ppt1.id, 189)
        self.assertEqual(self.ppt2.id, 77)

        self.assertEqual(self.ppt1.name, 'Houseboat')
        self.assertEqual(self.ppt2.name, 'Motels')

        self.assertEqual(self.ppt1.partner.name, 'Booking.com')
        self.assertEqual(self.ppt2.partner.name, 'Booking.com')


class PartnerPropertyMappingModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        pg1 = PropertyGroup.objects.create(id=1, name='Hotels')
        rbo = Brand.objects.create(
            id=1,
            name="RentByOwner.com",
            alias="RENTBYOWNER",
            key="RBO",
            date="2020-02-20T11:22:28Z",
            sort_order=13,
            created_at="2023-08-04T05:50:03.921Z",
            updated_at="2023-08-04T05:50:03.921Z"
        )

        pt1 = PropertyType.objects.create(
            id=1,
            name="Bed_Breakfast",
            brand=rbo,
            brand_type="rentals",
            create_date="2023-08-04T08:50:46.288Z",
            update_date="2023-08-04T08:50:46.288Z",
        )
        pt1.accommodation_type.add(pg1)

        partner = Partner.objects.create(
            id=1,
            name='Booking.com',
            key='BC',
            domain_name='booking.com',
            feed=11,
            sort_order=1
        )

        ppt1 = PartnerPropertyType.objects.create(
            id=69,
            name='Bed and breakfasts',
            partner=partner
        )


        ppm = PartnerPropertyMapping.objects.create(
            id=1,
            property_type=pt1,
            partner_property=ppt1,
        )
        cls.ppm = ppm


    @classmethod
    def tearDownClass(cls):
        PartnerPropertyMapping.objects.all().delete()
        PartnerPropertyType.objects.all().delete()
        PropertyType.objects.all().delete()
        Partner.objects.all().delete()
        Brand.objects.all().delete()
        PropertyGroup.objects.all().delete()

    def test_model_content(self):
        self.assertEqual(self.ppm.partner_property.name, 'Bed and breakfasts')
        self.assertEqual(self.ppm.property_type.name, 'Bed_Breakfast')
