import requests
import os
import json
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo 
from typing import List, Dict, Tuple
from dotenv import load_dotenv
load_dotenv()

# BASE_URL = os.environ.get("BASE_URL", "http://localhost:3000")

def parse_datetime(dt_str: str) -> datetime:
    """Parse datetime string from Google Calendar API format."""
    return datetime.fromisoformat(dt_str)

def load_calendar_data(
    time_min=None,
    time_max=None
) -> Dict:
    """
    Query Google Calendar FreeBusy API and return busy time data.
    Args:
        calendar_ids: List of calendar IDs to query.
        time_min: ISO8601 string for the start time.
        time_max: ISO8601 string for the end time.
    Returns:
        Dict response from the FreeBusy API.
    """
    # Set default time_min and time_max if not provided
    now = datetime.now(ZoneInfo('America/Los_Angeles'))
    if time_min is None:
        time_min = now.isoformat()
    if time_max is None:
        time_max = (now + timedelta(days=7)).isoformat()

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
        "timezone": "PST",
        "items": [{"id": "primary"}]
    }
    response = requests.post(url, headers=headers, json=body)
    response.raise_for_status()
    with open("calendar_pull.json", "w") as f:
        json.dump(response.json(), f, indent=2)
    return response.json()

def get_free_slots(
    time_min=None,
    time_max=None
) -> Dict:
    """
    Given Google Calendar free/busy data, find available time slots.
    
    Args:
        calendar_id: Google Calendar ID        
    Returns:
        Dictionary with dates as keys and lists of free time slots as values
    """

    calendar_data = load_calendar_data(time_min, time_max)["calendars"]["primary"]
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
        date = s.strftime("%Y-%m-%d")
        by_date.setdefault(date, []).append((s, e))
    for date, times in by_date.items():
        # Merge overlapping/contiguous busy intervals
        merged = []
        for s, e in sorted(times):
            if not merged or merged[-1][1] < s:
                merged.append([s, e])
            else:
                merged[-1][1] = max(merged[-1][1], e)
            # Work bounds (make tz-aware by using tzinfo from first interval)
            d = datetime.strptime(date, "%Y-%m-%d")
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
                free_slots.setdefault(date, []).extend(slots)
    
    return free_slots


# Example usage:
if __name__ == "__main__":
    # Get free slots
    free_slots = get_free_slots(time_min="2025-04-28T00:00:00.000+00:00", time_max="2025-04-28T23:59:00.000+00:00")
    
    # Print the results
    print(json.dumps(free_slots, indent=2))