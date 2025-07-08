from __future__ import annotations

import logging
import sys

import structlog


def setup_logging(level: str) -> None:
    shared_processors: list[structlog.types.Processor] = [
        # Adds contextual data from structlog's contextvars.
        structlog.contextvars.merge_contextvars,
        # Adds local thread-specific context.
        structlog.threadlocal.merge_threadlocal,
        # Adds log level, timestamp, etc.
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        # Allows for string formatting like "Hello %s"
        structlog.stdlib.PositionalArgumentsFormatter(),
        # If the log record is a string, it will be wrapped in a dict
        # with the key "event".
        structlog.processors.UnicodeDecoder(),
        structlog.processors.StackInfoRenderer(),
    ]

    # Configure structlog to wrap the standard library's logging.
    structlog.configure(
        processors=[
            # This processor is special and must be first. It bridges
            # the standard library's logging with structlog.
            structlog.stdlib.filter_by_level,
            *shared_processors,
            # This processor must be last. It prepares the log record
            # for rendering.
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        # Use a dict-based logger factory for performance.
        logger_factory=structlog.stdlib.LoggerFactory(),
        # Use a wrapper class for a more powerful logger.
        wrapper_class=structlog.stdlib.BoundLogger,
        # Caches the logger for performance.
        cache_logger_on_first_use=True,
    )

    # Configure the renderer for the output.
    formatter = structlog.stdlib.ProcessorFormatter(
        # These processors are only applied to records created by
        # structlog, not records from the standard library.
        foreign_pre_chain=shared_processors,
        processor=structlog.dev.ConsoleRenderer(
            colors=True, exception_formatter=structlog.dev.plain_traceback
        ),
    )

    # The handler sends the log records to a destination, like the console.
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    # The root logger is the top-level logger. All other loggers
    # inherit from it. By configuring the root logger, we capture
    # logs from all libraries (like discord.py, httpx, etc.).
    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    root_logger.setLevel(level)

    logging.getLogger("discord").setLevel(logging.WARNING)
    logging.getLogger("websockets").setLevel(logging.WARNING)
