"""app/utils/logging_config.py — Standard library structured logging."""
import logging
import json
import sys

def configure_logging(level: str = "INFO") -> None:
    logging.basicConfig(
        stream=sys.stdout,
        level=getattr(logging, level.upper(), logging.INFO),
        format='{"time":"%(asctime)s","level":"%(levelname)s","logger":"%(name)s","message":"%(message)s"}',
        datefmt="%Y-%m-%dT%H:%M:%S",
    )

def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
