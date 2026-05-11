import dj_database_url
from decouple import config

from .base import *  # noqa: F403

DEBUG = False
DATABASES["default"] = dj_database_url.config(  # type: ignore[assignment]  # noqa: F405
    default=config("DATABASE_URL"),
    conn_max_age=600,
    conn_health_checks=True,
)

SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
