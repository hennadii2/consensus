from common.config.secret_manager import SecretId, access_secret
from loguru import logger
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

DEV_NOTIFS_CHANNEL_ID = "C05SCQCT6SU"


def send_dev_notification(message):
    client = WebClient(token=access_secret(SecretId.SLACK_DEVBOT_API_KEY))

    try:
        _ = client.chat_postMessage(channel=DEV_NOTIFS_CHANNEL_ID, text=message)
    except SlackApiError as e:
        logger.error(e)
