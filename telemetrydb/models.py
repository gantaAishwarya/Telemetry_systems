from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict
from telemetrydb.config import Sample

@dataclass
class Channel:
    """
    Represents a telemetry channel as a time series of timestamped float values.
    """
    name: str
    samples: List[Sample] = field(default_factory=list)

@dataclass
class Asset:
    """
    Represents a telemetry dataset (asset) which contains multiple channels.
    """
    name: str
    channels: Dict[str, Channel] = field(default_factory=dict)
