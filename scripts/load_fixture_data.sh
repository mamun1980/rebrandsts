#!/usr/bin/env bash

# python manage.py flush --noinput

python manage.py migrate

python manage.py createsuperuser_if_none_exists --user=admin --password=Admin123

python manage.py loaddata data/sts_data_prod.json

#python manage.py loaddata apps/partners/fixtures/partners_full.json
#python manage.py loaddata apps/brands/fixtures/brands_full.json
#python manage.py loaddata apps/property/fixtures/property_full.json
#python manage.py loaddata apps/sqs/fixtures/sqs_full.json
#python manage.py loaddata apps/sts/fixtures/sts_full.json
#python manage.py loaddata apps/amenities/fixtures/AmenityTypeCategory.json