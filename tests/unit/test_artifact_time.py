from datetime import UTC, datetime
import unittest

from diamonddust.artifact_time import format_artifact_time, format_artifact_time_slug


class ArtifactTimeTests(unittest.TestCase):
    def test_format_artifact_time_uses_utc_plus_8_offset(self) -> None:
        value = datetime(2026, 5, 28, 4, 30, 5, tzinfo=UTC)

        self.assertEqual(format_artifact_time(value), "2026-05-28T12:30:05+08:00")

    def test_format_artifact_time_slug_uses_utc_plus_8_clock(self) -> None:
        value = datetime(2026, 5, 28, 4, 30, 5, tzinfo=UTC)

        self.assertEqual(format_artifact_time_slug(value), "20260528T123005UTC8")


if __name__ == "__main__":
    unittest.main()
