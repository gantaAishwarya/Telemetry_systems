import matplotlib.pyplot as plt
from datetime import datetime, timedelta, timezone
from telemetry_db.data_manager import TelemetryDataManager
from config import load_config
from typing import Optional, List


def plot_asset(ts_client: TelemetryDataManager, asset_name: str,
               start: Optional[datetime] = None,
               stop: Optional[datetime] = None,
               channel_names: Optional[List[str]] = None):
    """
    Plot all channels of a given asset within an optional time range.
    """
    asset = ts_client.query_asset(asset_name=asset_name,
                                  channel_names=channel_names,
                                  start=start,
                                  stop=stop)

    if not asset.channels:
        print("No channels found in asset.")
        return

    plt.figure(figsize=(12, 6))
    for channel in asset.channels:
        if not channel.samples:
            continue
        timestamps, values = zip(*channel.samples)
        plt.plot(timestamps, values, label=channel.name, marker='o', linestyle='-')

    plt.title(f"All Channels from Asset '{asset_name}'")
    plt.xlabel("Time")
    plt.ylabel("Value")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()



def plot_channel(ts_client: TelemetryDataManager, asset_name: str, channel_name: str,
                 start=None, stop=None):
    """
    Query a specific asset/channel and plot its time-series data.
    """
    asset = ts_client.query_asset(asset_name=asset_name, channel_names=[channel_name], start=start, stop=stop)

    if not asset:
        raise ValueError('Asset not found.')
    for channel in asset.channels:
        if channel.name == channel_name:
            samples = channel.samples
            timestamps, values = zip(*samples) if samples else ([], [])
    
    if not timestamps:
        print("No data to plot.")
        return

    plt.figure(figsize=(10, 5))
    plt.plot(timestamps, values, marker='o', linestyle='-')
    plt.title(f"Channel '{channel_name}' from Asset '{asset_name}'")
    plt.xlabel("Time")
    plt.ylabel("Value")
    plt.grid(True)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    config = load_config()

    ts = TelemetryDataManager(
        url=config["url"],
        token=config["token"],
        org=config["org"],
        bucket=config["bucket"]
    )

    # Plot channel data from asset 'MLOX_3' for the last 10 minutes
    stop_time = datetime.now(timezone.utc)
    start_time = stop_time - timedelta(minutes=10)

    plot_channel(ts, asset_name="MLOX_1", channel_name="vlox", start=start_time, stop=stop_time)
    plot_asset(ts, asset_name="MLOX_1", )
    ts.close()
