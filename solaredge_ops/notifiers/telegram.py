"""Telegram push transport.

Telegram was chosen as the primary "push to the repair team's phones" channel
because it requires no paid service, supports group chats (so the whole crew gets
the message instantly and can discuss/claim it inline), has a dead-simple HTTP API,
and both iOS/Android clients deliver native push notifications for free.

This class is a thin transport: it knows how to deliver text to a given chat ID,
nothing more. Deciding *which* chat gets *which* message is the job of
`notifiers.router.AlertRouter`, driven by the `recipients` directory in the config.

Setup (for the README): create a bot via @BotFather, add it to the team's group
chat, then send any message in that chat and call
`https://api.telegram.org/bot<token>/getUpdates` once to read the chat_id.
"""
from __future__ import annotations

import logging

import requests

from ..config import TelegramConfig

logger = logging.getLogger(__name__)

API_URL = "https://api.telegram.org/bot{token}/sendMessage"


class TelegramNotifier:
    name = "telegram"

    def __init__(self, config: TelegramConfig, session: requests.Session | None = None):
        self.config = config
        self.session = session or requests.Session()

    def send(self, chat_id: str, text: str) -> None:
        if not self.config.bot_token or not chat_id:
            logger.warning("Telegram not fully configured (missing bot_token/chat_id) - dropping message")
            return
        url = API_URL.format(token=self.config.bot_token)
        response = self.session.post(
            url,
            json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"},
            timeout=15,
        )
        if response.status_code != 200:
            logger.error("Telegram send failed: HTTP %s - %s", response.status_code, response.text[:300])
