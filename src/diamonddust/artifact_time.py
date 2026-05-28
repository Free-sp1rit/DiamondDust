"""Artifact timestamp helpers."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone


ARTIFACT_TIMEZONE = timezone(timedelta(hours=8), "UTC+08:00")


def artifact_now() -> str:
    return format_artifact_time(datetime.now(ARTIFACT_TIMEZONE))


def artifact_timestamp_slug() -> str:
    return format_artifact_time_slug(datetime.now(ARTIFACT_TIMEZONE))


def format_artifact_time(value: datetime) -> str:
    aware = _as_artifact_timezone(value)
    return aware.replace(microsecond=0).isoformat()


def format_artifact_time_slug(value: datetime) -> str:
    aware = _as_artifact_timezone(value)
    return aware.strftime("%Y%m%dT%H%M%SUTC8")


def _as_artifact_timezone(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=ARTIFACT_TIMEZONE)
    return value.astimezone(ARTIFACT_TIMEZONE)
