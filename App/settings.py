from pathlib import Path
import os
from vercel_blob import VercelBlob
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent



DEFAULT_FILE_STORAGE = 'vercel_blob.VercelBlobStorage'
VERCEL_BLOB_READ_WRITE_TOKEN = 'vercel_blob_rw_XkXFe8Qx26azIf6W_W8lZUkExIURrGDWLZf6Uy4wT8WFRcS'
DEFAULT_FILE_STORAGE = 'vercel_blob.VercelBlobStorage'
VERCEL_BLOB_READ_WRITE_TOKEN = os.environ.get('VERCEL_BLOB_READ_WRITE_TOKEN')
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '*53H&St0]7BG;lCv{=y7Pd2c#o#s{w:pn5smlj3e#&We>5bew}'


# SECURITY WARNING: don't run with debug turned on in production!
AUTH_USER_MODEL = 'CraftCoin.CustomUser'
DEBUG = False
ALLOWED_HOSTS = ['.vercel.app', 'localhost', '127.0.0.1']

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': '/tmp/django-errors.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'ERROR',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}

LOGOUT_REDIRECT_URL = '/'  # Esto redirigirá a la página de inicio después del cierre de sesión

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'craftcoin.web@gmail.com'
EMAIL_HOST_PASSWORD = 'sysf wdle mxtp bhij'


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    #Apps
    
    
    'CraftCoin',
    'Server1',
    'VoxelCraft',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'CraftCoin.middleware.ExceptionLoggingMiddleware',
]

ROOT_URLCONF = 'App.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'App.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'verceldb',
        'USER': 'default',
        'PASSWORD': '6fDYS8kUOqIT',
        'HOST': 'ep-odd-morning-a45eoleu.us-east-1.aws.neon.tech',
        'PORT': '5432',
        'OPTIONS': {
            'sslmode': 'require',
        },
        'CONN_MAX_AGE': 0,
    }
}
# En settings.py
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5 MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5 MB


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


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

# Media files
MEDIA_URL = 'https://your-project-name.vercel.app/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
