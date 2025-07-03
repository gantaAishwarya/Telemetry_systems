from influxdb_client import InfluxDBClient
from telemetrydb.config import load_config, setup_logger
from influxdb_client.client.write_api import SYNCHRONOUS

setup_logger()
config = load_config()

class InfluxConnector:
    def __init__(self):
        self.url = config["url"]
        self.token = config["token"]
        self.org = config["org"]
        self.bucket = config["bucket"]
        self.client = InfluxDBClient(url=self.url, token=self.token, org=self.org)

    def get_write_api(self):
        return self.client.write_api(write_options=SYNCHRONOUS)

    def get_query_api(self):
        return self.client.query_api()

    def close(self):
        self.client.close()
