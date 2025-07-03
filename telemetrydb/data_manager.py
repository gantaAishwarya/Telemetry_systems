from datetime import datetime, timezone
from telemetrydb.client import InfluxConnector
from typing import List, Dict, Optional
from influxdb_client import Point
from telemetrydb.models import Asset, Channel
from telemetrydb.config import Sample

class TelemetryDataManager:

    def __init__(self):
        self.conn = InfluxConnector()
        self.write_api = self.conn.get_write_api()
        self.query_api = self.conn.get_query_api()
        self.bucket = self.conn.bucket
        self.org = self.conn.org

    def _format_flux_time(self, timestamp: Optional[datetime], default: str) -> str:
        if not timestamp:
            return default
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)
        return timestamp.isoformat()
    
    @staticmethod
    def _ensure_utc(timestamp: datetime) -> datetime:
        """
        Ensure the datetime is timezone-aware in UTC.
        """
        if timestamp.tzinfo is None:
            return timestamp.replace(tzinfo=timezone.utc)
        else:
            return timestamp.astimezone(timezone.utc)


    def create_asset(self, asset_name: str, initial_channels: Dict[str, List[Sample]]) -> Asset:
        """
        Create an asset with one or more channels and write the initial samples to InfluxDB.
        """
        if not initial_channels:
            raise ValueError("An asset must have at least one channel with samples")

        channels = {}
        all_points = []

        for channel_name, samples in initial_channels.items():
            if not samples:
                raise ValueError(f"Channel '{channel_name}' must have at least one sample")

            # Normalize timestamps and create points
            points = [
                Point(asset_name)
                .tag("channel", channel_name)
                .field("value", value)
                .time(self._ensure_utc(timestamp))
                for timestamp, value in samples
            ]

            all_points.extend(points)
            channels[channel_name] = Channel(name=channel_name, samples=samples)

        # Batch write all points
        self.write_api.write(bucket=self.bucket, org=self.org, record=all_points)

        return Asset(name=asset_name, channels=channels)

    def create_channel(
        self,
        asset_name: str,
        channel_name: str,
        samples: Optional[List[Sample]] = None
    ) -> Channel:
        """
        Create a channel and add samples if provided.
        """
        samples = samples or []

        points = [
            Point(asset_name)
            .tag("channel", channel_name)
            .field("value", value)
            .time(self._ensure_utc(timestamp))
            for timestamp, value in samples
        ]

        if points:
            self.write_api.write(bucket=self.bucket, org=self.org, record=points)

        return Channel(name=channel_name, samples=samples)


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

            start_str = self._format_flux_time(start, default="0")
            stop_str = self._format_flux_time(stop, default="now()")

            flux = f'''
                from(bucket: "{self.bucket}")
                |> range(start: {start_str}, stop: {stop_str})
                |> filter(fn: (r) => r["_measurement"] == "{asset_name}")
                |> filter(fn: (r) => r["_field"] == "value")
            '''

            if channel_names:
                filters = ' or '.join([f'r["channel"] == "{ch}"' for ch in channel_names])
                flux += f'\n  |> filter(fn: (r) => ({filters}))'

            flux += '\n  |> sort(columns: ["_time"])'

            tables = self.query_api.query(flux)

            channel_data: Dict[str, List[Sample]] = {}

            for table in tables:
                for record in table.records:
                    ch_name = record.values.get("channel")
                    timestamp = record.get_time()
                    value = record.get_value()

                    if ch_name not in channel_data:
                        channel_data[ch_name] = []

                    channel_data[ch_name].append((timestamp, value))

            channels = {
                ch_name: Channel(name=ch_name, samples=samples)
                for ch_name, samples in channel_data.items()
            }

            return Asset(name=asset_name, channels=channels)


    def close(self):
        """Close the client connection."""
        self.conn.close()