## ReBrand Search Tweaking System

### How to set up locale dev environment

1. Create database and set database credentials into .env file
2. Clone the repo
```commandline
$ git clone git@code.lefttravel.com:vrs/re-brand-sts.git
$ cd  re-brand-sts
```
3. Rename .env_sample to .env and set values
```commandline
SITE_ENV=dev
SECRET_KEY
DEBUG=True

TRUSTED_ORIGIN=XXX,XXX,XXX
LOCATION_API_BASE_URL=XXX
COMMON_CORN_API_BASE_URL=XXX
TOKEN=XXX

DB_HOST=XXXX
DB_PORT=XXXX
DB_NAME=XXXX
DB_USER_NAME=XXXX
DB_USER_PASSWORD=XXXX

ANALYTICS_DB_HOST=XXX
ANALYTICS_DB_PORT=XXX
ANALYTICS_DB_NAME=XXX
ANALYTICS_DB_USER_NAME=XXX
ANALYTICS_DB_USER_PASSWORD=XXX

PD_AWS_TABLE_NAME=XXX
PD_AWS_SERVICE_NAME=XXX
PD_AWS_REGION_NAME=XXX
PD_AWS_ACCESS_KEY_ID=XXX
PD_AWS_SECRET_ACCESS_KEY=XXX

OPEN_API_KEY=XXX
```
4. Create and activate virtual environment
```commandline
$ python3 -m venv .venv
$ source .venv/bin/activate
```
5. Install project requirements for dev environment
```commandline
(.venv)$ pip install -r requirements/dev.txt
```
6. Migrate Database & Load fixture data
```commandline
(.venv)$ bash scripts/load_fixture_data.sh
```
7. Install and start memcached server
8. Start the development server
```commandline
(.venv)$ python manage.py runserver
```
- You can now visit site at: http://127.0.0.1:8000
- You can visit admin site at: http://127.0.0.1:8000/admin/
  - username: admin
  - password: Admin123
9. Run coverage test
```commandline
(.venv)$ python manage.py test
(.venv)$ coverage run --source='.' manage.py test
(.venv)$ coverage report
```

### Setup development environment using docker compose

1. Create database and set database credentials into .env file
2. Clone the repo
```commandline
$ git clone git@code.lefttravel.com:vrs/re-brand-sts.git
$ cd  re-brand-sts
```
3. Create database and set database credentials into .env file
```commandline
SITE_ENV=dev
SECRET_KEY
DEBUG=True

TRUSTED_ORIGIN=XXX,XXX,XXX
LOCATION_API_BASE_URL=XXX
COMMON_CORN_API_BASE_URL=XXX
TOKEN=XXX

DB_HOST=XXXX
DB_PORT=XXXX
DB_NAME=XXXX
DB_USER_NAME=XXXX
DB_USER_PASSWORD=XXXX

ANALYTICS_DB_HOST=XXX
ANALYTICS_DB_PORT=XXX
ANALYTICS_DB_NAME=XXX
ANALYTICS_DB_USER_NAME=XXX
ANALYTICS_DB_USER_PASSWORD=XXX

PD_AWS_TABLE_NAME=XXX
PD_AWS_SERVICE_NAME=XXX
PD_AWS_REGION_NAME=XXX
PD_AWS_ACCESS_KEY_ID=XXX
PD_AWS_SECRET_ACCESS_KEY=XXX

OPEN_API_KEY=XXX
```
4. Run the following script and your dev environment is ready to go

```commandline
$ docker-compose up -d --build
```

N.P If database not connected place DB_HOST=ip_address in .env file

5. Setup Production / beta / Staging Server   
[Deployments](deployment/eb/README.md)

6. Added pipeline
