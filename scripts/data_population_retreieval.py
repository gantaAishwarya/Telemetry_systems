import logging
import random
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Tuple, Optional
from telemetrydb.data_manager import TelemetryDataManager
from telemetrydb.models import Asset
from telemetrydb.config import setup_logger

Sample = Tuple[datetime, float]

# Configure logger
setup_logger()

logger = logging.getLogger(__name__)

def print_asset(asset: Asset) -> None:
    """Print asset information."""
    logger.info(f"📡 Asset: {asset.name} (channels: {len(asset.channels)})")
    for ch_name, channel in asset.channels.items():
        logger.info(f"  🔧 Channel: {ch_name} - Samples: {len(channel.samples)}")
        for ts, val in channel.samples:
            logger.info(f"{asset.name} -> {ch_name} {ts.isoformat()} -> {val}")
    logger.info("-" * 2)


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


def test_create_assets(ts_client: TelemetryDataManager, assets: List[Dict[str, Dict[str, List[Sample]]]]) -> None:
    """
    Test creating assets and channels using TelemetrySystems.
    """

    for asset_data in assets:
        asset_name = asset_data.get("name")
        channels = asset_data.get("channels", {})

        # Create asset
        try:
            asset = ts_client.create_asset(asset_name, channels)
            logger.info(f"Created asset '{asset_name}' with channels: {list(asset.channels.keys())}")
        except Exception as e:
            logger.error(f"Failed to create asset '{asset_name}': {e}")
            continue

        # Add additional channels
        for ch_name in ["new_channel_1", "new_channel_2"]:
            try:
                samples = generate_samples(duration_seconds=2)
                channel = ts_client.create_channel(asset_name, ch_name, samples)
                logger.info(f"Created channel '{ch_name}' with {len(channel.samples)} samples in asset '{asset_name}'")
            except Exception as e:
                logger.error(f"Failed to create channel '{ch_name}' in asset '{asset_name}': {e}")



def test_query_asset(ts_client: TelemetryDataManager, asset_name: str, start: Optional[datetime] = None, stop: Optional[datetime] = None, channel_names: Optional[List[str]] = None) -> None:
    """
    Runs a series of queries on the specified asset with different filters and prints the results.
    """
    try:
        def query_and_print(**kwargs):
            asset = ts_client.query_asset(asset_name, **kwargs)
            print_asset(asset)

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

    start_time = datetime.now(timezone.utc) - timedelta(days=1)
    ts = TelemetryDataManager()

    assets_to_create = [
        {
            "name": "MLOX_3",
            "channels": {
                "vmet": generate_samples(60),
                "vlox": generate_samples(60),
                "pcc": generate_samples(60),
            },
        },
        {
            "name": "MLOX_4",
            "channels": {
                "vmet": generate_samples(60),
                "vlox": generate_samples(60),
                "pcc": generate_samples(60),
            },
        },
    ]

    test_create_assets(ts, assets_to_create)
    test_query_asset(ts, 'MLOX_3', start=start_time, stop=datetime.now(timezone.utc))
    ts.close()
