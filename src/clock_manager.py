from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

_UTC = timezone.utc


def _utcnow():
    """Naive UTC datetime; used for arithmetic with cached naive UTC values."""
    return datetime.now(_UTC).replace(tzinfo=None)

# Look this far ahead when scanning for the next DST transition. ~13 months
# covers every annual transition once even if a zone has just transitioned.
_DST_SCAN_DAYS = 400
# Re-scan a city's transition cache no more than once per this interval.
_DST_REFRESH = timedelta(hours=6)


class ClockManager:
    def __init__(self):
        # Cache: timezone_str -> (computed_at_utc, next_fall_back_utc or None)
        # Only fall-back transitions ("clocks go back" / move toward winter)
        # are tracked - that is what the user asked us to alert on.
        self._dst_cache = {}

    def get_time_for_city(self, city_name, timezone_str):
        """Get current time for a specific timezone with DST support."""
        try:
            tz = ZoneInfo(timezone_str)
            now = datetime.now(tz)
            return now
        except Exception as e:
            print(f"Error getting time for {city_name} ({timezone_str}): {e}")
            return None

    def format_time_24h(self, dt):
        """Format datetime object as 24-hour time (HH:MM:SS)."""
        if dt is None:
            return "--:--:--"
        return dt.strftime("%H:%M:%S")

    def format_date_ddmm(self, dt):
        """Format datetime object as DD-MM."""
        if dt is None:
            return "-----"
        return dt.strftime("%d-%m")

    def _next_fall_back(self, timezone_str):
        """Return UTC datetime of the next 'fall-back' DST transition for
        this zone (when the offset DECREASES - i.e. clocks go back toward
        standard / winter time), or None if the zone has no DST or no
        fall-back is scheduled within the scan window.

        Result is cached for ``_DST_REFRESH`` so repeated calls in the
        per-second update loop are essentially free.
        """
        cached = self._dst_cache.get(timezone_str)
        now_utc = _utcnow()
        if cached and now_utc - cached[0] < _DST_REFRESH:
            return cached[1]

        try:
            tz = ZoneInfo(timezone_str)
        except Exception:
            self._dst_cache[timezone_str] = (now_utc, None)
            return None

        # Walk forward day-by-day comparing utcoffset(); the first day
        # whose offset is SMALLER than the prior day is a fall-back.
        cursor = datetime.now(tz)
        prior_offset = cursor.utcoffset()
        result = None
        for _ in range(_DST_SCAN_DAYS):
            cursor = cursor + timedelta(days=1)
            offset = cursor.utcoffset()
            if offset is not None and prior_offset is not None and offset < prior_offset:
                # Found a fall-back day. We don't bother locating the exact
                # 02:00 instant - day granularity is fine for "X days until".
                result = cursor.astimezone(ZoneInfo("UTC")).replace(tzinfo=None)
                break
            prior_offset = offset

        self._dst_cache[timezone_str] = (now_utc, result)
        return result

    def days_until_fall_back(self, timezone_str):
        """Days (rounded down) until the next fall-back transition, or
        None if no transition within the scan window. 0 means today."""
        nxt = self._next_fall_back(timezone_str)
        if nxt is None:
            return None
        delta = nxt - _utcnow()
        return max(0, delta.days)

    def get_clock_data(self, city_name, timezone_str):
        """Get formatted time and date data for a single city."""
        dt = self.get_time_for_city(city_name, timezone_str)
        days = self.days_until_fall_back(timezone_str)
        if days is None or days > 7:
            dst_alert = ""
        elif days == 0:
            dst_alert = "DST ends today"
        elif days == 1:
            dst_alert = "DST ends tomorrow"
        else:
            dst_alert = f"DST ends in {days} days"
        return {
            "city": city_name,
            "timezone": timezone_str,
            "time": self.format_time_24h(dt),
            "date": self.format_date_ddmm(dt),
            "dst_alert": dst_alert,
            "valid": dt is not None,
        }

    def get_all_clock_data(self, cities):
        """Get clock data for all cities in the list."""
        return [self.get_clock_data(city["name"], city["timezone"]) for city in cities]
