import ssl

from pathlib import Path
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = config('SECRET_KEY', 'django-insecure-q!w7-p$)f0phuw%k4shop=_2py31_p5*%6dxqgiq#l$ehpi0zp')

DEBUG = config('DEBUG', default=False, cast=bool)

ENV = config('SITE_ENV', 'dev')

ALLOWED_HOSTS = [ip.strip() for ip in config('ALLOWED_HOSTS', '*').split(',')]

CSRF_TRUSTED_ORIGINS = [ip.strip() for ip in config('TRUSTED_ORIGIN', 'http://127.0.0.1:8000').split(',')]

INSTALLED_APPS = [
    'api',
    'apps.accounts',
    'apps.partners.apps.PartnersConfig',
    'apps.brands',
    'apps.property',
    'apps.amenities.apps.AmenitiesConfig',
    'apps.sqs.apps.SqsConfig',
    'apps.sts.apps.StsConfig',
    'apps.dashboard.apps.DashboardConfig',
    'apps.analytics',

    'simple_history',
    'admin_auto_filters',
    'more_admin_filters',
    'rest_framework',
    'admin_extra_buttons',
    'django_ace',
    'django_json_widget',
    
    'jazzmin',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',



]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'core/templates'
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

DATABASES = {
    'default': {
        "ENGINE": "django.db.backends.postgresql",
        'NAME': config('DB_NAME', ''),
        'USER': config('DB_USER_NAME', ''),
        'PASSWORD': config('DB_USER_PASSWORD', ''),
        'HOST': config('DB_HOST', ''),
        'PORT': config('DB_PORT', default=5432, cast=int)
    },
    'analytics': {
        "ENGINE": 'django.db.backends.postgresql',
        'NAME': config('ANALYTICS_DB_NAME', ''),
        'USER': config('ANALYTICS_DB_USER_NAME', ''),
        'PASSWORD': config('ANALYTICS_DB_USER_PASSWORD', ''),
        'HOST': config('ANALYTICS_DB_HOST', ''),
        'PORT': config('ANALYTICS_DB_PORT', default=5432, cast=int)
    }
}

SIMPLE_HISTORY_REVERT_DISABLED = True

DATABASE_ROUTERS = ["core.db_router.AnalyticsRouter"]

LOGOUT_REDIRECT_URL = '/login/'

LOGIN_REDIRECT_URL = '/'

DATA_UPLOAD_MAX_NUMBER_FIELDS = 50000

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

STATIC_URL = 'static/'

STATIC_ROOT = BASE_DIR / 'staticfiles'

STATICFILES_DIRS = (BASE_DIR / 'core/static',)

MEDIA_URL = 'media/'

MEDIA_ROOT = BASE_DIR / 'public/media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_PERMISSION_CLASSES': [
        # 'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
        'rest_framework.permissions.AllowAny',
    ]
}

# Celery settings

# CELERY_ACCEPT_CONTENT = ['application/json']
#
# CELERY_RESULT_SERIALIZER = 'json'
#
# CELERY_TASK_SERIALIZER = 'json'
#
# CELERY_BROKER_URL = "redis://localhost:6379"
#
# CELERY_RESULT_BACKEND = 'django-db'
#
# CELERY_CACHE_BACKEND = 'django-cache'

CACHE_TIMEOUT = 86400 * 180

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.memcached.PyMemcacheCache",
        'LOCATION': '127.0.0.1:11211',
        "TIMEOUT": 86400
    }
}

AZZMIN_UI_TWEAKS = {
    "theme": "superhero",
    "dark_mode_theme": "darkly",
}


JAZZMIN_SETTINGS = {
    # title of the window (Will default to current_admin_site.site_title if absent or None)
    "site_title": "STS Admin",

    # Title on the login screen (19 chars max) (defaults to current_admin_site.site_header if absent or None)
    "site_header": "STS",

    # Title on the brand (19 chars max) (defaults to current_admin_site.site_header if absent or None)
    "site_brand": "STS",

    # Logo to use for your site, must be present in static files, used for brand on top left
    "site_logo": None,

    # Logo to use for your site, must be present in static files, used for login form logo (defaults to site_logo)
    "login_logo": None,

    # Logo to use for login form in dark themes (defaults to login_logo)
    "login_logo_dark": None,

    # CSS classes that are applied to the logo above
    "site_logo_classes": "img-circle",

    # Relative path to a favicon for your site, will default to site_logo if absent (ideally 32x32 px)
    "site_icon": None,

    # Welcome text on the login screen
    "welcome_sign": "Welcome to the STS",

    # Copyright on the footer
    "copyright": "W3Engineers Ltd",

    # List of model admins to search from the search bar, search bar omitted if excluded
    # If you want to use a single search field you dont need to use a list, you can use a simple string
    # "search_model": ["auth.User", "auth.Group"],

    # Field name on user model that contains avatar ImageField/URLField/Charfield or a callable that receives the user
    "user_avatar": None,

    ############
    # Top Menu #
    ############

    # Links to put along the top menu
    "topmenu_links": [

        # Url that gets reversed (Permissions can be added)
        {"name": "API",  "url": "/api/", "permissions": ["sts.view_ratioset"]},

        # App with dropdown menu to all its models pages (Permissions checked against models)
        {"app": "sqs"},
        {"app": "brands"},
        {"app": "property"},
        {"app": "analytics"},
        {"app": "partners"},
        {"app": "amenities"},

    ],

    #############
    # User Menu #
    #############

    # Additional links to include in the user menu on the top right ("app" url type is not allowed)
    # "usermenu_links": [
    #     {"name": "Support", "url": "https://github.com/farridav/django-jazzmin/issues", "new_window": True},
    #     {"model": "auth.user"}
    # ],

    #############
    # Side Menu #
    #############

    # Whether to display the side menu
    "show_sidebar": True,

    # Whether to aut expand the menu
    "navigation_expanded": True,

    # Hide these apps when generating side menu e.g (auth)
    "hide_apps": ["sqs", "brands", "property", "analytics", "partners", "amenities"],

    # Hide these models when generating side menu (e.g auth.user)
    "hide_models": [],

    # List of apps (and/or models) to base side menu ordering off of (does not need to contain all apps/models)
    "order_with_respect_to": ["auth", "sts"],

    # Custom links to append to app groups, keyed on app name
    "custom_links": {
        "sts": [
            {
                "name": "Property Mapping",
                "url": "drag-and-drop-partner-property-mapping",
                "icon": "fas fa-keyboard",
                "permissions": ["sts.view_partnerpropertymapping"]
            },
            {
                "name": "Amenity Mapping",
                "url": "amenity-type-mapping",
                "icon": "fas fa-layer-group",
                "permissions": ["sts.view_partneramenitytype", "sts.view_amenitytypecategory"]
            },
            {
                "name": "Check S3 RatioSet Status",
                "url": "admin:check-s3-ratio-set-status",
                "icon": "fas fa-file-code",
                "permissions": ["sts.view_brandlocationdefinedsetsratio"]

            }
        ]
    },
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        "sts.location": "fas fa-street-view",
        "sts.device": "fas fa-mobile",
        "sts.locationtype": "fas fa-globe",
        "sts.leavebehindpopunderrules": "fas fa-location-arrow",
        "sts.searchlocation": "fas fa-map",
        "sts.ratiolocation": "fas fa-map",
        "sts.ratioset": "fas fa-percent",
        "sts.partnerratio": "fas fa-handshake",
        "sts.ratiogroup": "fas fa-object-group",
        "sts.predictedratio": "fas fa-people-arrows",
        "sts.brandlocationdefinedsetsratio": "fas fa-compass",
        "sts.duplicatepropertypartnerorder": "fas fa-clone",
    },
    # Icons that are used when one is not manually specified
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",

    #################
    # Related Modal #
    #################
    # Use modals instead of popups
    "related_modal_active": False,

    #############
    # UI Tweaks #
    #############
    # Relative paths to custom CSS/JS scripts (must be present in static files)
    "custom_css": None,
    "custom_js": None,
    # Whether to link font from fonts.googleapis.com (use custom_css to supply font otherwise)
    "use_google_fonts_cdn": True,
    # Whether to show the UI customizer on the sidebar
    "show_ui_builder": False,

    ###############
    # Change view #
    ###############
    # Render out the change view as a single form, or in tabs, current options are
    # - single
    # - horizontal_tabs (default)
    # - vertical_tabs
    # - collapsible
    # - carousel
    "changeform_format": "horizontal_tabs",
    # override change forms on a per modeladmin basis
    "changeform_format_overrides": {"auth.user": "collapsible", "auth.group": "vertical_tabs"},
    # Add a language dropdown into the admin
    "language_chooser": False,
}