import os
from pathlib import Path
import environ

# Initialize environment variables
env = environ.Env()
environ.Env.read_env()  # Read .env file

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Security settings
SECRET_KEY = env('DJANGO_SECRET_KEY')
DEBUG = True    

ALLOWED_HOSTS = [
    "192.168.31.33", 
    "assanjfinal.onrender.com",
    "127.0.0.1",
    "localhost",
]


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'allauth',   
    'allauth.account',  
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google', 
    'django.contrib.sites',
    'rest_framework',
    'rest_framework.authtoken',
    'rest_auth',
    'embed_video',
    'core.templatetags',
    'crispy_forms',
    'crispy_bootstrap5',
    'core.apps.CoreConfig',
    'users.apps.UsersConfig',
    # 'storages',
]

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)

SITE_ID = 14
ACCOUNT_ADAPTER = 'allauth.account.adapter.DefaultAccountAdapter'
SOCIALACCOUNT_ADAPTER = 'allauth.socialaccount.adapter.DefaultSocialAccountAdapter'
SOCIALACCOUNT_AUTO_SIGNUP = True


LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
CRISPY_TEMPLATE_PACK = 'bootstrap5'

# Social account providers
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        }
    }
}

MIDDLEWARE = [
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'core.middleware.SingleDeviceLoginMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
]

# STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
AUTH_USER_MODEL = 'users.CustomUser'

ROOT_URLCONF = 'Main.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates/')],
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
# MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

WSGI_APPLICATION = 'Main.wsgi.application'

import dj_database_url
import os

DATABASES = {
    'default': dj_database_url.config(
        default='postgresql://new1234_user:Pj2dVMG9rzi26P8aPhilmoVjv43qVT34@dpg-cvsjonre5dus7396b100-a.oregon-postgres.render.com/new1234',
        conn_max_age=600,
        ssl_require=True
    )
}


# Password validation
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

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = '/staticfile/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfile')
# STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'


# # Google Maps API Key
# GOOGLE_MAPS_API_KEY = env('GOOGLE_MAPS_API_KEY')

# Media
MEDIA_URL = '/images/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'static/images/')

CSRF_TRUSTED_ORIGINS = [
    "http://192.168.31.33:8000",  # ✅ Add this
    "http://127.0.0.1:8000",
    "http://localhost:8000",
]

CORS_ALLOWED_ORIGINS = [
    "http://127.0.0.1:8000",
    "http://localhost:8000",
    "https://assanj.in",
]


# # AWS Settings

# AWS_ACCESS_KEY_ID = 'AKIAZOZQF7MB5BGNNT4W'
# AWS_SECRET_ACCESS_KEY = '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'
# AWS_STORAGE_BUCKET_NAME = 'assanjbuck'
# AWS_S3_SIGNATURE_NAME='s3v4'
# AWS_S3_REGION_NAME = 'eu-north-1'
# AWS_QUERYSTRING_AUTH = False
# DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'




# Email Backend
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_TLS = True
EMAIL_HOST = env('EMAIL_HOST')
EMAIL_PORT = env('EMAIL_PORT')
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')



##PAYMENTS##
RAZORPAY_KEY_ID = "rzp_test_AkSfYqzbTkz3rH"
RAZORPAY_KEY_SECRET = "Xm5OK0qqXnFz6BgX2CLkOEpE"
