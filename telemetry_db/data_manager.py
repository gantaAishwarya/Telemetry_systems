from datetime import datetime, timezone
from typing import List, Dict, Optional
from telemetry_db.models import Asset, Channel
from influxdb_client import InfluxDBClient
from config import setup_logger
import logging
from telemetry_db.types import Sample

# Configure logger
setup_logger()
logger = logging.getLogger(__name__)

class TelemetryDataManager:

    def __init__(self, url: str, token: str, org: str, bucket: str):
        """Initialize the TelemetryDataManager with InfluxDB connection settings."""
        self.url = url
        self.token = token
        self.org = org
        self.bucket = bucket
        self.client = InfluxDBClient(url=self.url, token=self.token, org=self.org)
        self.write_api = self.client.write_api
        self.query_api = self.client.query_api


    def close(self):
        self.client.close()

    @staticmethod
    def _ensure_utc(timestamp: datetime) -> datetime:
        """
        Ensure the datetime is timezone-aware in UTC.
        """
        if timestamp.tzinfo is None:
            return timestamp.replace(tzinfo=timezone.utc)
        else:
            return timestamp.astimezone(timezone.utc)
        
    def _format_flux_time(self, timestamp: Optional[datetime], default: str) -> str:
        if not timestamp:
            return default
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)
        return timestamp.isoformat()
    
    def create_asset(self, asset_name: str, initial_channels: Dict[str, List[Sample]]) -> Asset:
        """
        Create an asset with one or more channels and write the initial samples to InfluxDB.
        """
        if not initial_channels:
            raise ValueError("An asset must have at least one channel with samples")

        asset = Asset(manager=self, asset_name= asset_name, initial_channels=initial_channels)

        if asset.exists():
            raise ValueError("An asset with this name already exists.")

        # Creating new asset
        asset.create()
        return asset

    def create_channel(
        self,
        asset_name: str,
        channel_name: str,
        samples: Optional[List[Sample]] = None
    ) -> Channel | None:
        """
        Create a channel and add samples if provided.
        """
        samples = samples or []

        asset = Asset(manager=self, asset_name= asset_name)

        if not asset.exists():
            return None
        
        if any(ch.name == channel_name for ch in getattr(asset, "channels", [])):
            raise ValueError(f"Channel '{channel_name}' already exists in asset '{asset_name}'.")

        channel = Channel(name=channel_name, samples=samples)
        asset.add_channel(channel=channel)
        return channel


    def query_asset(
                self,
                asset_name: str,
                channel_names: Optional[List[str]] = None,
                start: Optional[datetime] = None,
                stop: Optional[datetime] = None
        ) -> Asset:
            """
            Query an asset channels data from InfluxDB within a time range.
            """
            if not asset_name:
                raise ValueError("asset_name is required")
            
            asset = Asset(manager=self,asset_name=asset_name)

            if not asset.exists():
                raise ValueError(f"Asset '{asset_name}' does not exist.")

            tables = asset.query(channel_names=channel_names,start=start,stop=stop)

            channel_data: Dict[str, List[Sample]] = {}

            for table in tables:
                for record in table.records:
                    ch_name = record.values.get("channel")
                    timestamp = record.get_time()
                    value = record.get_value()

                    if ch_name not in channel_data:
                        channel_data[ch_name] = []

                    channel_data[ch_name].append((timestamp, value))
                    
            return Asset(self,asset_name=asset_name, initial_channels=channel_data)
    

    def print_asset(self, asset: Asset) -> None:
        """Print asset information."""
        logger.info(f"Asset: {asset.name} (channels: {len(asset.channels)})")
        for channel in asset.channels:
            logger.info(f"Channel: {channel.name} - Samples: {len(channel.samples)}")
            for ts, val in channel.samples:
                logger.info(f"{asset.name} -> {channel.name} {ts.isoformat()} -> {val}")
        logger.info("-" * 2)