from pathlib import Path
from configparser import ConfigParser
from datetime import datetime
import json


def log_timestamp(message: str) -> None:
    """Print message with timestamp prefix."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {message}")


def load_config(config_path: str) -> ConfigParser:
    """Load configuration from INI file."""
    config = ConfigParser()
    config_file = Path(__file__).parent.parent / config_path

    if not config_file.exists():
        raise FileNotFoundError(f"Config file not found: {config_file}")

    config.read(config_file)
    return config

def get_type(uuid_prefix: str) -> str:
    def load_json(path):
        with open(Path(path)) as f:
            return json.load(f)

    REQUIREMENT_UUIDS = {obj["uuid"] for obj in load_json("../data/requirement_uuid_mapping.json")}
    SUPPLEMENTAL_UUIDS = {obj["uuid"] for obj in load_json("../data/supplemental_uuid_mapping.json")}
    TEST_UUIDS = {obj["uuid"] for obj in load_json("../data/test_uuid_mapping.json")}

    if uuid_prefix in REQUIREMENT_UUIDS:
        return "requirement"
    if uuid_prefix in SUPPLEMENTAL_UUIDS:
        return "supplemental"
    if uuid_prefix in TEST_UUIDS:
        return "test"
    return "unknown"