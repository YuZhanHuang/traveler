import logging.config
import os
import datetime as dt
from logging import LogRecord

from delorean import Delorean
from structlog.types import EventDict
from logging.handlers import TimedRotatingFileHandler

import structlog

from .helper import log_json
from .constants import LOG_FILE, LOG_PATH, LOG_LEVEL, LOCAL_TZ
from typing import (
    Any,
    Dict,
    Optional,
)


def make_stamper(fmt: Optional[str], utc: bool, key: str):
    def stamper(event_dict: EventDict) -> EventDict:
        event_dict[key] = Delorean(timezone=LOCAL_TZ).datetime.isoformat()
        return event_dict

    return stamper


class CustomizedTimestamper(structlog.processors.TimeStamper):
    def __init__(self, fmt: str = 'iso', key: str = 'datetime_tz', utc: bool = False):
        super().__init__(fmt, utc, key)
        self._stamper = make_stamper(fmt, utc, key)

    def __setstate__(self, state: Dict[str, Any]) -> None:
        self.fmt = state["fmt"]
        self.utc = state["utc"]
        self.key = state["key"]
        self._stamper = make_stamper(**state)


class RequireDebugTrue(logging.Filter):
    def filter(self, record: LogRecord) -> bool:
        return os.environ.get('FLASK_CONFIG', 'production') == 'development'


class RequireDebugFalse(logging.Filter):
    def filter(self, record: LogRecord) -> bool:
        return os.environ.get('FLASK_CONFIG', 'production') != 'development'


class CustomizedTimedRotatingHandler(TimedRotatingFileHandler):
    def __init__(self, filename, when='h', interval=1, backupCount=0,  # noqa
                 encoding='utf-8', delay=False, utc=True, atTime=None,  # noqa
                 errors=None):
        super().__init__(filename, when, interval, backupCount,
                         encoding, delay, utc, atTime, errors)

    def rotation_filename(self, default_name):
        now = dt.datetime.now()
        return f'{now.strftime("%Y-%m-%dT%H:%M:%S")}-{LOG_FILE}_info.log'


logging.config.dictConfig({
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "()": structlog.stdlib.ProcessorFormatter,
            "processor": structlog.processors.JSONRenderer(serializer=log_json),
        },
        "plain": {
            "()": structlog.stdlib.ProcessorFormatter,
            "processor": structlog.dev.ConsoleRenderer(colors=False),
        },
        "colored": {
            "()": structlog.stdlib.ProcessorFormatter,
            "processor": structlog.dev.ConsoleRenderer(colors=False),
        },
    },
    "filters": {
        "require_debug_true": {
            "()": RequireDebugTrue,
        },
        "require_debug_false": {
            "()": RequireDebugFalse,
        },
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "json",
        },
        "info": {
            "level": "INFO",
            "formatter": "json",
            "filename": f'{LOG_PATH}/{LOG_FILE}_info.log',
            "()": "logging.handlers.TimedRotatingFileHandler",
            "when": "D",
            "interval": 1,
            "backupCount": 21,
        },
        "error": {
            "level": "ERROR",
            "formatter": "json",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": f"{LOG_PATH}/{LOG_FILE}_error.log",
            "mode": "a",
            "backupCount": 5,
            "maxBytes": 10485760
        },
    },
    "loggers": {
        "admin_dealer": {
            "handlers": ["console", "info", "error"],
            "level": LOG_LEVEL,
            "propagate": True,
        },
    }
})

customized_timestamper = CustomizedTimestamper()

processors = [
    customized_timestamper,
    structlog.stdlib.filter_by_level,  # If log level is too low, abort pipeline and throw away log entry.
    structlog.stdlib.add_logger_name,  # Add the name of the logger to event dict.
    structlog.stdlib.add_log_level,  # Add log level to event dict.
    structlog.stdlib.PositionalArgumentsFormatter(),  # Perform %-style formatting.
    # If the "stack_info" key in the event dict is true, remove it and
    # render the current stack trace in the "stack" key.
    structlog.processors.StackInfoRenderer(),
    # If the "exc_info" key in the event dict is either true or a
    # sys.exc_info() tuple, remove "exc_info" and render the exception
    # with traceback into the "exception" key.
    structlog.processors.format_exc_info,
    structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
]

structlog.configure_once(
    processors=processors,
    context_class=structlog.threadlocal.wrap_dict(dict),
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,  # noqa
    cache_logger_on_first_use=True,
)

get_logger = structlog.get_logger
