"""
Django settings for embitel_framework project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
location = lambda x: os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', x)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '%%*(sc+j4!noi65(haug-t0n3sdb97#p#k!2=_u=8ymmj&*8of'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []

LOGIN_URL = '/login'

MEDIA_ROOT = '/home/embadmin/Documents/django_apps/django_experiments/embitel/media/'
PROFILE_PICS_PATH = MEDIA_ROOT + 'profile_pics/'
MEDIA_URL = '/media/'
#STATIC_ROOT = ''
#STATIC_URL = '/static/'

STATICFILES_DIRS = (
'/home/embadmin/Documents/django_apps/django_experiments/embitel/' ,  
)
STATIC_ROOT = location('media/')

TEMPLATE_DIRS = (
    location('templates'),
)
# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'south',
    'embitel_framework',
    'push_notifications',
)

GCM_POST_URL = 'https://android.googleapis.com/gcm/send'
PUSH_NOTIFICATIONS_SETTINGS = {
        "GCM_API_KEY": "AIzaSyCxS-2NivPBjO9M05lyOgxcLEa0mzrEa5s",
        #"APNS_CERTIFICATE": "/home/embadmin/Documents/django_apps/django_experiments/embitel/embitel_framework/cer_and_p12.pem",
        "APNS_CERTIFICATE": "/home/embadmin/pushparaja.pem",
}
MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'embitel_framework.urls'

WSGI_APPLICATION = 'embitel_framework.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'push', # Or path to database file if using sqlite3.
        'USER': 'push', # Not used with sqlite3.
        'PASSWORD': 'push',#'84adf87feae4a6f0c63f0a3df7d6c456', # Not used with sqlite3.
        'HOST': '127.0.0.1', # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '', # Set to empty string for default. Not used with sqlite3.
    },
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

#TIME_ZONE = 'UTC'
TIME_ZONE = 'Asia/Calcutta'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'

MESSAGE_SEPARATER = '<!@#$%)(*&^>'
