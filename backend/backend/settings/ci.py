from backend.settings.base import *  # noqa
from backend.settings.development import *  # noqa

REST_FRAMEWORK = {**REST_FRAMEWORK, "DEFAULT_THROTTLE_CLASSES": []}
