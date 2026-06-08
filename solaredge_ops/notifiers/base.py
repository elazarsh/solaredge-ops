"""Notifier interface — anything that can deliver an Alert or a report somewhere."""
from __future__ import annotations

from abc import ABC, abstractmethod

from ..models import Alert


class Notifier(ABC):
    name: str = "notifier"

    @abstractmethod
    def send_alert(self, alert: Alert) -> None:
        """Push a single real-time alert (new problem or resolved problem)."""

    def send_text(self, subject: str, body: str) -> None:
        """Send a free-form message (used for reports / digests). Optional to implement."""
        raise NotImplementedError(f"{self.name} does not support free-form messages")
