import random
from datetime import datetime, timedelta, timezone
from typing import List, Dict
from telemetry_db.data_manager import TelemetryDataManager
from telemetry_db.types import Sample
from config import setup_logger ,load_config
import logging

# Configure logger
setup_logger()
logger = logging.getLogger(__name__)


def generate_samples(duration_seconds: int, frequency_hz: int = 1) -> List[Sample]:
    """
    Generate dummy samples for the given duration and frequency.
    """
    now = datetime.now(timezone.utc)
    interval = 1 / frequency_hz
    samples = [
        (
            now - timedelta(seconds=duration_seconds - i * interval),
            round(random.uniform(0, 100), 4),
        )
        for i in range(duration_seconds * frequency_hz)
    ]
    return samples


def mock_create_assets(ts_client: TelemetryDataManager, assets: List[Dict[str, Dict[str, List[Sample]]]]) -> None:
    """
    Creats assets and channels using TelemetrySystems package with the provided mock data.
    """

    for asset_data in assets:
        asset_name = asset_data.get("name")
        channels = asset_data.get("channels", {})

        # Create asset
        try:
            asset = ts_client.create_asset(asset_name, channels)
            logger.info(f"Created asset '{asset_name}' with channels: {list(asset.channels)}")
        except Exception as e:
            logger.error(f"Failed to create asset '{asset_name}': {e}")
            continue

        # Add additional channels
        for ch_name in ["new_channel_1", "new_channel_2"]:
            try:
                samples = generate_samples(duration_seconds=60)
                channel = ts_client.create_channel(asset_name, ch_name, samples)
                logger.info(f"Created channel '{ch_name}' with {len(channel.samples)} samples in asset '{asset_name}'")
            except Exception as e:
                logger.error(f"Failed to create channel '{ch_name}' in asset '{asset_name}': {e}")

if __name__ == "__main__":

    config = load_config()

    influxdb_url = config["url"]
    influxdb_token = config["token"]
    influxdb_org = config["org"]
    influxdb_bucket = config["bucket"]

    ts = TelemetryDataManager(url=influxdb_url,token=influxdb_token,org=influxdb_org,bucket=influxdb_bucket)

    start_time = datetime.now(timezone.utc) - timedelta(days=1)

    mock_assets_to_create = [
        {
            "name": "MLOX_1",
            "channels": {
                "vmet": generate_samples(60),
                "vlox": generate_samples(60),
                "pcc": generate_samples(60),
            },
        },
        {
            "name": "MLOX_2",
            "channels": {
                "vmet": generate_samples(60),
                "vlox": generate_samples(60),
                "pcc": generate_samples(60),
            },
        },
    ]

    mock_create_assets(ts, mock_assets_to_create)
    ts.close()
