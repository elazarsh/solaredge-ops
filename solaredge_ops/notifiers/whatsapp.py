"""WhatsApp push transport via Green API (https://green-api.com).

Green API is a free-tier WhatsApp gateway that works with a regular WhatsApp
account (no Business API required).  It supports personal chats and group chats.

Setup:
  1. Register at https://green-api.com and create a free instance.
  2. In the instance dashboard, scan the QR code with your WhatsApp.
  3. Copy idInstance and apiTokenInstance to config.yaml.
  4. To find a group chat ID:
       - Add the instance's number to your WhatsApp group.
       - Call: GET https://api.green-api.com/waInstance{id}/getChats/{token}
       - Look for the group entry; its chatId ends with @g.us, e.g. 120363XXXXX@g.us
     Or simply use a personal phone number as chatId: 972501234567@c.us
       (country code + number, no +, suffix @c.us)

The chatId per recipient goes in config.yaml under recipients[].whatsapp_chat_id.
"""
from __future__ import annotations

import logging

import requests

from ..config import WhatsAppConfig

logger = logging.getLogger(__name__)

_SEND_URL = "https://api.green-api.com/waInstance{instance_id}/sendMessage/{api_token}"


class WhatsAppNotifier:
    name = "whatsapp"

    def __init__(self, config: WhatsAppConfig, session: requests.Session | None = None):
        self.config = config
        self.session = session or requests.Session()

    def send(self, chat_id: str, text: str) -> None:
        """Send a plain-text message to chat_id (group or personal)."""
        if not self.config.instance_id or not self.config.api_token or not chat_id:
            logger.warning(
                "WhatsApp not fully configured (missing instance_id / api_token / chat_id) - dropping message"
            )
            return
        url = _SEND_URL.format(
            instance_id=self.config.instance_id,
            api_token=self.config.api_token,
        )
        try:
            resp = self.session.post(
                url,
                json={"chatId": chat_id, "message": text},
                timeout=15,
            )
            if resp.status_code != 200:
                logger.error(
                    "WhatsApp send failed: HTTP %s - %s", resp.status_code, resp.text[:300]
                )
            else:
                data = resp.json()
                if data.get("idMessage"):
                    logger.debug("WhatsApp message sent to %s: idMessage=%s", chat_id, data["idMessage"])
                else:
                    logger.warning("WhatsApp: unexpected response: %s", data)
        except requests.RequestException as exc:
            logger.error("WhatsApp request error: %s", exc)
