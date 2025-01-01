from pathlib import Path
import os
from django.urls import reverse_lazy


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
CORE_ASSETS =  BASE_DIR/'core/'
PWA_SERVICE_WORKER_PATH = os.path.join(CORE_ASSETS, 'static/js', 'service-worker.js')



# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-6b5_3h*ky_aibfn)bfgx!vqwovnkgx43b(341v!!t6f##q7nmx'


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    #third party 
    'corsheaders',
    'django_extensions',
    "pwa",

    # developer apps
    'users',
    'reptrack_trace',
    'reports',
]


PWA_APP_NAME = 'Reps Track and Trace'
PWA_APP_DESCRIPTION = "Track stock consumption and movement across locations"
PWA_APP_THEME_COLOR = '#000000'
PWA_APP_BACKGROUND_COLOR = '#ffffff'
PWA_APP_DISPLAY = 'standalone'
PWA_APP_SCOPE = '/'
PWA_APP_START_URL = '/'
PWA_APP_ORIENTATION = 'any'
PWA_APP_CATEGORIES = ['utilities']
PWA_APP_STATUS_BAR = 'default'
PWA_APP_PREFER_RELATED_APPLICATIONS = False
PWA_APP_ICONS = [
    {
        'src': '/static/images/logo192x192.png',
        'sizes': '192x192',
        'type': 'image/png'
    },
    {
        'src': '/static/images/logo512x512.png',
        'sizes': '512x512',
        'type': 'image/png'
    }
]
PWA_APP_SPLASH_SCREEN = [
    {
        'src': '/static/images/screenshot_1.png',
        'sizes': '1080x1920',
        'type': 'image/png',
        'form_factor': 'wide'
    }
]



PWA_APP_DIR = 'ltr'
PWA_APP_LANG = 'en-US'


AUTH_USER_MODEL = 'users.User'



MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'users.middleware.RoleMiddleware', 

]

CORS_ALLOW_ALL_ORIGINS = False

ROOT_URLCONF = 'main_conf.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [CORE_ASSETS/'templates'],
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



WSGI_APPLICATION = 'main_conf.wsgi.application'


CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DB_DIR = CORE_ASSETS/'sql_db'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': DB_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


LOGIN_URL = reverse_lazy('reptrack_trace:login')
LOGOUT_REDIRECT_URL = reverse_lazy('reptrack_trace:logout')
LOGIN_REDIRECT_URL = reverse_lazy('reptrack_trace:home')




# The URL to access static files
STATIC_URL = '/static/'

# Additional directories where Django will look for static files
STATICFILES_DIRS = [
    CORE_ASSETS / "static",  # Ensure this points to the correct "static" directory in your project
]

# Directory where Django collects all static files for deployment
STATIC_ROOT = CORE_ASSETS / "staticfiles"

MEDIA_URL = '/media/'
MEDIA_ROOT = CORE_ASSETS / 'media' 


if DEBUG:
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'
else:
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Static Files Finders
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

# Additional Security Settings for SSL
#USE_X_FORWARDED_HOST = True
#SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Increase timeout in Django as well
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
DATA_UPLOAD_MAX_NUMBER_FIELDS = 10240

#SESSION_COOKIE_SECURE = True
#CSRF_COOKIE_SECURE = True
#SECURE_SSL_REDIRECT = True


# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
