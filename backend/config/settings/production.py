from typing import cast

from decouple import Csv, config

from .base import *  # noqa: F403

DEBUG = False
SECRET_KEY = config("SECRET_KEY")

ALLOWED_HOSTS = cast(
    list[str], config("ALLOWED_HOSTS", default=".railway.app", cast=Csv())
)  # noqa: F405

DATABASES = {  # noqa: F405
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",  # noqa: F405
    }
}

# Security
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = config("SECURE_SSL_REDIRECT", default=True, cast=bool)
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# HSTS
SECURE_HSTS_SECONDS = config("SECURE_HSTS_SECONDS", default=31536000, cast=int)
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Extra Security Headers
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = "DENY"
SECURE_REFERRER_POLICY = "same-origin"
SECURE_CROSS_ORIGIN_OPENER_POLICY = "same-origin"

# CSRF Trusted Origins
CSRF_TRUSTED_ORIGINS: list[str] = cast(
    list[str],
    config("CSRF_TRUSTED_ORIGINS", default="", cast=Csv()),
)

# Logging override for production
LOGGING["handlers"]["console"]["level"] = "INFO"  # noqa: F405
LOGGING["loggers"]["django"]["level"] = "INFO"  # noqa: F405

# Static files storage
# For production, we usually use WhiteNoise or a CDN.
# Using Django's default for now, but configured for manifest-based cache busting.
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.ManifestStaticFilesStorage",
    },
}
