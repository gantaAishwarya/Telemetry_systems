from __future__ import annotations
from typing import List, Dict, Optional, TYPE_CHECKING
from influxdb_client import Point
from datetime import datetime
from influxdb_client.client.write_api import SYNCHRONOUS
from telemetry_db.types import Sample
from influxdb_client.client.flux_table import FluxTable

if TYPE_CHECKING:
    from data_manager import TelemetryDataManager

class Asset:
    """
    Represents a telemetry dataset (asset) which contains multiple channels.
    """
    name: str
    channels: List[Channel]

    def __init__(self, manager: TelemetryDataManager, asset_name: str, initial_channels: Optional[Dict[str, List[Sample]]] = None):

        self.manager = manager
        self.name = asset_name
        self.channels = [] 
        if initial_channels:
            self.channels = [Channel(name=name, samples=samples) for name, samples in initial_channels.items()]
        self.write_api = self.manager.write_api(write_options=SYNCHRONOUS)
        self.query_api = self.manager.query_api()

    def __repr__(self) -> str:
        return f"Asset:{self.name}"

    def exists(self) -> bool:
        """
        Check if an asset with the current name already exists in InfluxDB.

        Returns:
            bool: True if the asset exists, False otherwise.
        """
        flux = f'''
            import "influxdata/influxdb/schema"
            schema.measurements(bucket: "{self.manager.bucket}")
            |> filter(fn: (r) => r._value == "{self.name}")
        '''

        result = self.query_api.query(flux)
        return any(table.records for table in result)

    def create(self):
        """Persists the Asset and related channels to DB."""
        all_points = []
        
        if not self.channels:
            raise ValueError("Asset must have at least one channel with samples.")

        for channel in self.channels:
            # Normalize timestamps and create points
            points = [
                Point(self.name)
                .tag("channel", channel.name)
                .field("value", value)
                .time(self.manager._ensure_utc(timestamp))
                for timestamp, value in channel.samples
            ]

            all_points.extend(points)

        # Batch write all points
        self.write_api.write(bucket=self.manager.bucket, org=self.manager.org, record=all_points)

    def query(self, channel_names: Optional[List[str]] = None,
                start: Optional[datetime] = None,
                stop: Optional[datetime] = None
        ) -> List[FluxTable]:
        """
            Query an asset channels data from InfluxDB within a time range.
        """

        start_str = self.manager._format_flux_time(start, default="0")
        stop_str = self.manager._format_flux_time(stop, default="now()")

        flux = f'''
            from(bucket: "{self.manager.bucket}")
            |> range(start: {start_str}, stop: {stop_str})
            |> filter(fn: (r) => r["_measurement"] == "{self.name}")
            |> filter(fn: (r) => r["_field"] == "value")
        '''

        if channel_names:
            filters = ' or '.join([f'r["channel"] == "{ch}"' for ch in channel_names])
            flux += f'\n  |> filter(fn: (r) => ({filters}))'


        flux += '''
            |> keep(columns: ["_time", "_value", "channel"])
            |> sort(columns: ["_time"])
        '''

        tables = self.query_api.query(flux)

        return tables

    def add_channel(self, channel: Channel) -> None:
        """
        Adds a new telemetry channel to the asset and writes its samples to InfluxDB.

        Args:
            channel (Channel): The channel to add with its associated samples.
        """
        if not channel or not channel.samples:
            return  # Nothing to write

        points = [
            Point(self.name)
            .tag("channel", channel.name)
            .field("value", value)
            .time(self.manager._ensure_utc(timestamp))
            for timestamp, value in channel.samples
        ]

        self.channels.append(channel)  # Add to internal list

        self.write_api.write(bucket=self.manager.bucket, org=self.manager.org, record=points)
    
class Channel:
    """
    Represents a telemetry channel as a time series of timestamped float values.
    """
    name: str
    samples: List[Sample]

    def __init__(self,name: str, samples:List[Sample]):
        self.name = name
        self.samples = samples

        if not samples:
            raise ValueError(f"Channel '{self.name}' must have at least one sample")
        
    def __repr__(self) -> str:
        return f"Channel:{self.name}"
