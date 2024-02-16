
# python manage.py collectstatic --noinput
#
# python manage.py flush --noinput

python manage.py migrate
#
python manage.py createsuperuser_if_none_exists --user=admin --password=Admin123

python manage.py load_partners_data

python manage.py load_partners_provider_data

python manage.py load_brands_data

python manage.py load_brands_dynamic_site_maps

python manage.py load_brands_static_site_maps

python manage.py load_data_for_property_group

python manage.py load_data_for_partner_property_types

python manage.py load_data_for_property_types_mapping

python manage.py load_data_for_setlist

python manage.py load_data_for_setlistes

python manage.py load_data_for_siteenableset

python manage.py load_data_for_siteenablesetses

python manage.py load_data_for_sqs

python manage.py load_data_for_device_type

python manage.py load_data_for_locations

python manage.py load_data_for_search_locations

python manage.py load_data_for_ratio_group

python manage.py load_data_for_location_ratio

python manage.py load_data_for_sts_ratio