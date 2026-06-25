import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any

import uuid
from datetime import date


class JSONEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, (uuid.UUID, datetime, date)):
            return str(o)
        try:
            return super().default(o)
        except TypeError:
            return str(o)


class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_data: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(
                record.created, tz=timezone.utc
            ).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
        }
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
            
        from app.core.context import client_ip_var
        log_data["ip_address"] = client_ip_var.get()

        # Capture custom extra parameters passed in logger calls
        standard_attrs = {
            "name",
            "msg",
            "args",
            "levelname",
            "levelno",
            "pathname",
            "filename",
            "module",
            "exc_info",
            "exc_text",
            "stack_info",
            "lineno",
            "funcName",
            "created",
            "msecs",
            "relativeCreated",
            "thread",
            "threadName",
            "processName",
            "process",
            "extra",
        }
        for key, val in record.__dict__.items():
            if key not in standard_attrs and not key.startswith("_"):
                log_data[key] = val

        return json.dumps(log_data, cls=JSONEncoder)


def setup_logging() -> None:
    root_logger = logging.getLogger()
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.INFO)

    # Force Uvicorn loggers to propagate to the root logger
    for logger_name in ("uvicorn", "uvicorn.access", "uvicorn.error"):
        logger = logging.getLogger(logger_name)
        logger.handlers = []
        logger.propagate = True
