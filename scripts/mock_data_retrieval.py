import random
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional
from telemetry_db.data_manager import TelemetryDataManager
from telemetry_db.types import Sample
from config import setup_logger ,load_config
import logging

# Configure logger
setup_logger()
logger = logging.getLogger(__name__)


def mock_query_asset(ts_client: TelemetryDataManager, asset_name: str, start: Optional[datetime] = None, stop: Optional[datetime] = None) -> None:
    """
    Runs a series of queries on the specified asset with different filters and prints the results.
    """
    try:
        def query_and_print(**kwargs):
            asset= ts_client.query_asset(asset_name=asset_name, **kwargs)
            ts.print_asset(asset=asset)
            

        logger.info(f"Running queries for asset '{asset_name}'")

        logger.info("\nCASE 1: All data (no filters)")
        query_and_print()

        logger.info("\nCASE 2: Single channel (pcc), all time")
        query_and_print(channel_names=["pcc"])

        logger.info("\nCASE 3: Multiple channels (vlox, vmet), all time")
        query_and_print(channel_names=["vlox", "vmet"])

        logger.info("\nCASE 4: All channels, sliced time")
        query_and_print(start=stop - timedelta(days=1), stop=stop)

        logger.info("\nCASE 5: Specific channel (vlox), sliced time")
        query_and_print(channel_names=["vlox"], start=stop - timedelta(minutes=1), stop=stop)

        logger.info("\nCASE 6: Only start time")
        query_and_print(start=start)

        logger.info("\nCASE 7: Only stop time")
        query_and_print(stop=stop)

    except Exception as e:
        logger.error(f"Failed to query asset '{asset_name}': {e}")

if __name__ == "__main__":

    config = load_config()

    INFLUXDB_URL = config["url"]
    INFLUXDB_TOKEN = config["token"]
    INFLUXDB_ORG = config["org"]
    INFLUXDB_BUCKET = config["bucket"]

    ts = TelemetryDataManager(url=INFLUXDB_URL,token=INFLUXDB_TOKEN,org=INFLUXDB_ORG,bucket=INFLUXDB_BUCKET)

    start_time = datetime.now(timezone.utc) - timedelta(days=1)

    mock_query_asset(ts, 'MLOX_1', start=start_time, stop=datetime.now(timezone.utc))
    ts.close()
