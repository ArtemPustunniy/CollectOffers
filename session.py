import logging
from pyrogram import Client
from config import API_ID, API_HASH, PHONE_NUMBER

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def get_session():
    app = Client("session_name", api_id=API_ID, api_hash=API_HASH, phone_number=PHONE_NUMBER)
    return app


def start_session(app):
    app.start()


if __name__ == "__main__":
    print("Hello")

