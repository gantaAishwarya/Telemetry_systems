# Telemetry_systems

**telemetry_db** is a lightweight Python package designed to manage telemetry time-series data using **InfluxDB 1.x**. It is ideal for use with test stands, simulations, or live systems. Data is organized into **Assets**, each containing multiple **Channels**, where each channel is a series of timestamped floating-point values.

---

## 📦 Features

- Define telemetry **Assets** with multiple **Channels**
- Store and retrieve `(timestamp, value)` time-series data
- Supports writing and querying using **InfluxDB 1.x**
- Mock/test data scripts included
- Easy to extend, test, and integrate into larger systems

---

## 🚀 Quickstart

### ✅ Prerequisites

- Python **3.10+**
- **Docker** (to run InfluxDB locally)
- **pip** (for Python package management)

---

### 🔧 Setup

#### 1. Start InfluxDB Locally

In the project root directory (`telemetry_systems`), run:

```bash
docker-compose up -d
```
This spins up a local InfluxDB 1.48 instance on http://localhost:8086 using the included docker-compose.yml


#### 2. Install Python Dependencies
Install all required Python packages by running:

```bash
pip install -r requirements.txt
```

#### 3. Populate, Query, and Test the Data

Run the data population script from root directory by executing:

```bash
python3 -m scripts.mock_data_population
```

##### What the script does:

- Adds 2 assets

- Each asset contains 5 channels

- Each channel has 60 samples (collected at 1Hz for 1 minute)


To check if data has been added succesfully run data retrieval script from root directory by executing:
```bash
 python3 -m scripts.mock_data_retrieval
```

##### What the script does:

- Queries asset data

- Filters data by time range or channel

- Prints the query results to the console

## Note: if you get an error, make sure you have a .env file, or create one based on .env.example.

# How to use the package:

## Install package by executing:

```bash
pip install .
```

This would create telemetry_db pacakge. Make sure you have a requirements.txt, config.py and .env file with your InfluxDB credentials.

## To use the package:

### Step 1. Initialize the Client

```bash
from telemetry_db.data_manager import TelemetryDataManager

ts = TelemetryDataManager(url=INFLUXDB_URL,token=INFLUXDB_TOKEN,org=INFLUXDB_ORG,bucket=INFLUXDB_BUCKET)
```

### Create Assets & Channels

```bash
from datetime import datetime, timezone

ts.create_asset("MLOX_3", {"vlox": [(datetime.now(timezone.utc), 42.0)]})

```
### Query Assets & Channels
```bash
asset = ts.query_asset("MLOX_3")
```
or
```bash
asset = ts.query_asset("MLOX_3", channel_names=["vlox"])
````
or 
```bash
from datetime import datetime, timedelta,

start_time = datetime.now(timezone.utc)-timedelta(days=1)
stop_time = datetime.now(timezone.utc)
asset = ts.query_asset("MLOX_3", channel_names=["vlox"], start=start_time, stop=stop_time)
```

### To see queried results data in readable format
``` bash
ts.print_asset(asset=asset) 
````
### Clean up using
```bash
ts.close()
```

### 🧪 View Data in InfluxDB UI

You can also inspect the data at the UI level by visiting:

[http://localhost:8086](http://localhost:8086)

- **Username:** `user`  
- **Password:** `userpass`

Once logged in, you should see something like this:

![InfluxDB Snapshot](images/snapshot.png)

### Example usage of the package can be viewed in scripts/generate_graph.py

Once execute the script from root directory using
```bash
python3 -m scripts generate_graph 
```` 

you should see something like this:

![InfluxDB Snapshot](images/channel.png)
![InfluxDB Snapshot](images/asset-channels.png)

## 📜 License

This project is licensed under the Apache License 2.0. See the [LICENSE](LICENSE) file for details.
