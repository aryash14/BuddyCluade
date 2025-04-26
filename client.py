import requests
import os
import json
from datetime import datetime, timedelta
from typing import Dict
import pytz
from dotenv import load_dotenv

load_dotenv()

# BASE_URL = os.environ.get("BASE_URL", "http://localhost:3000")

def parse_datetime(dt_str: str) -> datetime:
    """Parse datetime string from Google Calendar API format."""
    return datetime.fromisoformat(dt_str)

def load_calendar_data(
    date: str
) -> Dict:
    """
    Query Google Calendar FreeBusy API and return busy time data.
    Args:
        date: Date string in "YYYY-MM-DD" format.   
    Returns:
        Dict response from the FreeBusy API.
    """
    # Set default time_min and time_max if not provided
    date_obj = datetime.strptime(date, "%Y-%m-%d")
    pacific = pytz.timezone('America/Los_Angeles')
    target_date = pacific.localize(date_obj)
    # Convert to UTC and get the start of the day
    time_min = target_date.astimezone(pytz.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    # Get the end of the day in UTC (start of the next day - 1 second)
    time_max = (target_date + timedelta(days=1, seconds=-1)).astimezone(pytz.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
 
    access_token = os.environ.get("ACCESS_TOKEN")
    if not access_token:
        raise RuntimeError("GOOGLE_CALENDAR_TOKEN environment variable not set.")

    url = "https://www.googleapis.com/calendar/v3/freeBusy"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    body = {
        "timeMin": time_min,
        "timeMax": time_max,
        "timeZone": "America/Los_Angeles",
        "items": [{"id": "primary"}]
    }
    response = requests.post(url, headers=headers, json=body)
    response.raise_for_status()
    return response.json()

def get_free_slots(
    date: str = None
) -> Dict:
    """
    Given Google Calendar free/busy data, find available time slots.
    Args:
        date: Date string in "YYYY-MM-DD" format.   
    Returns:
        Dictionary with dates as keys and lists of free time slots as values
    """
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")
    calendar_data = load_calendar_data(date)["calendars"]["primary"]
    if not calendar_data or "busy" not in calendar_data:
        return {}

    work_start = 8
    work_end = 20
    busy_periods = calendar_data["busy"]
    free_slots = {}

    # Convert to datetime tuples
    intervals = [(parse_datetime(b["start"]), parse_datetime(b["end"])) for b in busy_periods]
    intervals.sort()
    # Group by date
    by_date = {}
    for s, e in intervals:
        d_str = s.strftime("%Y-%m-%d")
        by_date.setdefault(d_str, []).append((s, e))
    for d_str, times in by_date.items():
        # Merge overlapping/contiguous busy intervals
        merged = []
        for s, e in sorted(times):
            if not merged or merged[-1][1] < s:
                merged.append([s, e])
            else:
                merged[-1][1] = max(merged[-1][1], e)
        # Work bounds (make tz-aware by using tzinfo from first interval)
        d = datetime.strptime(d_str, "%Y-%m-%d")
        tzinfo = times[0][0].tzinfo if times and times[0][0].tzinfo else None
        day_start = d.replace(hour=work_start, minute=0, second=0, tzinfo=tzinfo)
        day_end = d.replace(hour=work_end, minute=0, second=0, tzinfo=tzinfo)
        cur = day_start
        slots = []
        for s, e in merged:
            if e <= day_start or s >= day_end:
                continue
            s = max(s, day_start)
            e = min(e, day_end)
            if cur < s:
                mins = (s - cur).total_seconds() / 60
                slots.append({
                    "start": cur.isoformat(),
                    "end": s.isoformat(),
                    "duration_minutes": int(mins)
                })
            cur = max(cur, e)
        if cur < day_end:
            mins = (day_end - cur).total_seconds() / 60
            slots.append({
                "start": cur.isoformat(),
                "end": day_end.isoformat(),
                "duration_minutes": int(mins)
            })
        if slots:
            free_slots.setdefault(d_str, []).extend(slots)
    return free_slots


# Example usage:
if __name__ == "__main__":
    # Get free slots
    free_slots = get_free_slots("2025-04-28")
    
    # Print the results
    print(json.dumps(free_slots, indent=2))