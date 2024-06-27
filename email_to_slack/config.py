# pyright: reportConstantRedefinition=false
import sys
from configparser import ConfigParser
from pathlib import Path

INCOMING_WEBHOOK_URL: str


def load_config() -> None:
    global INCOMING_WEBHOOK_URL
    config_file = Path(sys.argv[0]).parent / "email_to_slack.ini"
    config = ConfigParser()
    config.read(config_file)

    INCOMING_WEBHOOK_URL = config["Slack"]["WebhookURL"]


load_config()
