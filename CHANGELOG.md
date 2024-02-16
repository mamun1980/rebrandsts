# CHANGELOG


## Deploy: 04 (release)

- **Date:** 2024-02-15
- **Branch:** release/2.0.0
- **Environment:** release
- **Sequence:** 1
- **Changelog:**
    - Removed Celery & Redis and used sub-process
    - Replaced Redis Cache with Memcached
    - Update Bulk Create, Bulk Update, Clone, Bulk Clone functionality to use Sub-Process
    - Removed DynamoDB for prediction data read to use static json file from S3
    - Fix SetListES field to save json data
    - Unselect last item in multi-filter multi-select plugin issue
    - Moved Property Mapping, Amenity Mapping
    - Added Duplicate Property Partner Orders in API response
    - Some css design fix
    - Search Location issue fix
    - Check S3 RatioSet Status into admin site using Ajax call
    - Leave Behind & Pop Under redirection rules
- **Client Notice:**
    - `/prod/rbo.json`
    - `prediction_data/sts_prediction_data.json`
- **Deployment Instructions:**
    - Deploy

## Deploy: 03 (release)

- **Date:** 2024-01-15
- **Branch:** release/1.1.0
- **Environment:** release
- **Sequence:** 1
- **Changelog:**
    - Store STS ratio set to S3
- **Client Notice:**
    - `/prod/rbo.json`
- **Deployment Instructions:**
    - Deploy


## Deploy: 02 (release)

- **Date:** 2024-01-04
- **Branch:** release/1.0.1
- **Environment:** release
- **Sequence:** 1
- **Changelog:**
    - Enabled authentication for all pages of new dashboard
- **Client Notice:**
    - N/A
- **Deployment Instructions:**
    - Set `DEBUG = False` in `.env` file
    - Deploy

## Deploy: 01 (release)

- **Date:** 2023-12-27
- **Branch:** release/1.0.0
- **Environment:** release
- **Sequence:** 1
- **Changelog:**
    - Domain and UI changed
    - STS DB migration from MySQL to PG
    - STS Framework migration from Yii to Django
- **Client Notice:**
    - `/v3/get-sts-config/?site=PET` changed to `/api/get-sts-config/?site=PET`
    - `/site/get-mapped-property-types?partner=booking` changed to `/api/get-mapped-property-types?partner=bc`
    - `/property-type-refresh` changed to `/api/property-type-refresh`
- **Deployment Instructions:**
    - Ensure valid params `.env` from `.env_sample`
    - Deploy
