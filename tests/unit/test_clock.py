from __future__ import annotations

from datetime import UTC, date, datetime

import pytest

from icep.clock import FrozenClock, SystemClock, default_clock

pytestmark = pytest.mark.unit


def test_frozen_from_iso_date() -> None:
    assert FrozenClock.at("2026-07-07").today() == date(2026, 7, 7)


def test_frozen_from_epoch_string() -> None:
    assert FrozenClock.at("1783382400").today() == date(2026, 7, 7)


def test_frozen_from_iso_datetime_with_z() -> None:
    clock = FrozenClock.at("2026-07-07T09:30:00Z")
    assert clock.now() == datetime(2026, 7, 7, 9, 30, tzinfo=UTC)


def test_frozen_from_date_object() -> None:
    assert FrozenClock.at(date(2026, 1, 2)).today() == date(2026, 1, 2)


def test_frozen_from_datetime_object_gets_utc() -> None:
    assert FrozenClock.at(datetime(2026, 1, 2, 3, 4)).now().tzinfo is UTC


def test_default_clock_prefers_icep_now(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ICEP_NOW", "2026-07-07")
    monkeypatch.setenv("SOURCE_DATE_EPOCH", "0")
    assert default_clock().today() == date(2026, 7, 7)


def test_default_clock_falls_back_to_epoch(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ICEP_NOW", raising=False)
    monkeypatch.setenv("SOURCE_DATE_EPOCH", "1783382400")
    assert default_clock().today() == date(2026, 7, 7)


def test_default_clock_uses_system_clock_when_unset(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ICEP_NOW", raising=False)
    monkeypatch.delenv("SOURCE_DATE_EPOCH", raising=False)
    clock = default_clock()
    assert isinstance(clock, SystemClock)
    assert isinstance(clock.today(), date)
