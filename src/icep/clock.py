"""A single, injectable source of "now".

Every part of the platform reads the date through a :class:`Clock` instead of calling
``datetime.now()`` directly. That is what makes seeding, export and the tests byte-reproducible:
pin ``ICEP_NOW`` (an ISO date) or ``SOURCE_DATE_EPOCH`` (unix seconds) and the whole system
agrees on one "audit date".

>>> clock = FrozenClock.at("2026-07-07")
>>> clock.today().isoformat()
'2026-07-07'
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import UTC, date, datetime
from typing import Protocol, runtime_checkable

__all__ = [
    "Clock",
    "FrozenClock",
    "SystemClock",
    "default_clock",
    "ICEP_NOW_ENV",
    "SOURCE_DATE_EPOCH_ENV",
]

ICEP_NOW_ENV = "ICEP_NOW"
SOURCE_DATE_EPOCH_ENV = "SOURCE_DATE_EPOCH"


@runtime_checkable
class Clock(Protocol):
    """Anything that can report today's date and the current instant (UTC)."""

    def today(self) -> date: ...

    def now(self) -> datetime: ...


def _parse(text: str) -> datetime:
    """Parse an ISO date/datetime or a unix-epoch string into an aware UTC datetime."""
    raw = text.strip()
    if raw.isdigit():
        return datetime.fromtimestamp(int(raw), tz=UTC)
    iso = raw.replace("Z", "+00:00")
    if "T" not in iso:
        iso += "T00:00:00"
    return datetime.fromisoformat(iso)


@dataclass(frozen=True)
class FrozenClock:
    """A clock pinned to a fixed instant -- the backbone of deterministic output.

    >>> FrozenClock.at("2026-07-07").now().isoformat()
    '2026-07-07T00:00:00+00:00'
    >>> FrozenClock.at("1783382400").today().isoformat()
    '2026-07-07'
    """

    instant: datetime

    def today(self) -> date:
        return self.instant.date()

    def now(self) -> datetime:
        return self.instant

    @classmethod
    def at(cls, value: str | date | datetime) -> FrozenClock:
        """Build a frozen clock from an ISO string, a unix-epoch string, a date, or a datetime."""
        if isinstance(value, datetime):
            instant = value
        elif isinstance(value, date):
            instant = datetime(value.year, value.month, value.day)
        else:
            instant = _parse(value)
        if instant.tzinfo is None:
            instant = instant.replace(tzinfo=UTC)
        return cls(instant)


@dataclass(frozen=True)
class SystemClock:
    """A clock backed by the real wall clock -- used only when nothing is pinned."""

    def today(self) -> date:
        return datetime.now(tz=UTC).date()

    def now(self) -> datetime:
        return datetime.now(tz=UTC)


def default_clock() -> Clock:
    """Return the clock the CLI and web app should use.

    Resolution order (first hit wins): ``ICEP_NOW`` -> ``SOURCE_DATE_EPOCH`` -> real system clock.
    Pinning either environment variable makes seeding, export and tests fully reproducible.
    """
    pinned = os.environ.get(ICEP_NOW_ENV)
    if pinned:
        return FrozenClock.at(pinned)
    epoch = os.environ.get(SOURCE_DATE_EPOCH_ENV)
    if epoch:
        return FrozenClock.at(epoch)
    return SystemClock()
