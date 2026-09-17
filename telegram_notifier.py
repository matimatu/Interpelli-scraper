
from telegram import Bot
import configparser
from typing import Final

async def send_message(bot: Bot, chat_id: str, message: str) -> None:
    """Invia un messaggio di testo tramite Telegram."""
    await bot.send_message(
        chat_id=chat_id,
        text=message,
        disable_web_page_preview=False,
    )


def get_telegram_configuration() -> tuple[str, str]:
    """Legge token e chat ID dal file properties"""

    # Load BOT.properties
    config = configparser.ConfigParser()
    config.read('./BOT.properties')

    # Read values from BOT.properties
    BOT_TOKEN: Final = config.get('DEFAULT', 'BOT_TOKEN')
    CHAT_ID: Final = config.get('DEFAULT', 'CHAT_ID')

    if not BOT_TOKEN:
        raise RuntimeError("Variabile BOT_TOKEN non configurata")

    if not CHAT_ID:
        raise RuntimeError("Variabile CHAT_ID non configurata")

    return BOT_TOKEN, CHAT_ID