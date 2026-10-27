from datetime import datetime, timezone, date, timedelta
import zoneinfo
from backend.app.core.config import settings

class ClockService:
    def __init__(self, initial_iso: str = None):
        iso_str = initial_iso or settings.FROZEN_DEMO_CLOCK
        # Parse UTC datetime
        self._current_time = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        self._tz = zoneinfo.ZoneInfo(settings.DISPLAY_TIMEZONE)
        self._is_frozen = (settings.APP_ENV == "demo")

    def now_utc(self) -> datetime:
        if self._is_frozen:
            return self._current_time
        return datetime.now(timezone.utc)

    def now_iso(self) -> str:
        return self.now_utc().strftime("%Y-%m-%dT%H:%M:%SZ")

    def now_display(self) -> str:
        dt_local = self.now_utc().astimezone(self._tz)
        return dt_local.strftime("%d %B %Y at %H:%M IST")

    def today_local_date(self) -> date:
        return self.now_utc().astimezone(self._tz).date()

    def advance_time(self, days: int = 0, hours: int = 0, minutes: int = 0):
        if settings.APP_ENV != "demo":
            raise ValueError("Time travel is restricted to demo environment.")
        self._current_time += timedelta(days=days, hours=hours, minutes=minutes)

    def set_time(self, iso_str: str):
        if settings.APP_ENV != "demo":
            raise ValueError("Setting clock is restricted to demo environment.")
        self._current_time = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))

    def reset_to_seed(self):
        self._current_time = datetime.fromisoformat(settings.FROZEN_DEMO_CLOCK.replace("Z", "+00:00"))

clock_service = ClockService()
