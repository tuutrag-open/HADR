from pathlib import Path
from configparser import ConfigParser
from datetime import datetime


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