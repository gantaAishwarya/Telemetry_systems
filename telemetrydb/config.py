import logging
import sys
import os
from datetime import datetime
from typing import Tuple

logger = logging.getLogger(__name__)

# Defining shared variables
Timestamp = datetime
Value = float
Sample = Tuple[Timestamp, Value]


def setup_logger():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)]
    )

def load_env_var(name: str) -> str:
    val = os.getenv(name)
    if not val:
        logger.error(f"Missing required environment variable: {name}")
        sys.exit(1)
    return val

def load_config():
    return {
        "token": load_env_var("INFLUXDB_TOKEN"),
        "url": load_env_var("INFLUXDB_URL"),
        "org": load_env_var("INFLUXDB_ORG"),
        "bucket": load_env_var("INFLUXDB_BUCKET"),
    }
