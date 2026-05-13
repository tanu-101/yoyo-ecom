from .base import *  # noqa: F403

DEBUG = True

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",  # noqa: F405
    }
}

# Add file logging for local development
LOGGING["handlers"]["file"] = {  # noqa: F405
    "level": "DEBUG",
    "class": "logging.FileHandler",
    "filename": BASE_DIR / "debug.log",  # noqa: F405
    "formatter": "verbose",
}
LOGGING["loggers"]["apps"]["handlers"].append("file")  # noqa: F405
