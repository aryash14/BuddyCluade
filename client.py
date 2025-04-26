import requests
import os
import json
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo 
from typing import List, Dict, Tuple, Optional, Union
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

def create_calendar_event(
    summary: str,
    start_time: Union[str, datetime],
    end_time: Union[str, datetime],
    description: Optional[str] = None,
    location: Optional[str] = None,
    attendees: Optional[List[Dict[str, str]]] = None,
    recurrence: Optional[List[str]] = None,
    calendar_id: str = "primary",
    timezone: str = "America/Los_Angeles",
    send_notifications: bool = True
) -> Dict:
    """
    Create a calendar event using the Google Calendar API.
    
    Args:
        summary: Title of the event
        start_time: Start time (ISO datetime string or datetime object)
        end_time: End time (ISO datetime string or datetime object)
        description: Event description
        location: Physical location of the event
        attendees: List of dictionaries with attendee emails, e.g. [{"email": "person@example.com"}]
        recurrence: List of RRULE strings for recurring events
        calendar_id: Calendar identifier (default: "primary")
        timezone: Timezone for the event
        send_notifications: Whether to send notifications to attendees
        
    Returns:
        Dict with the created event details
    """
    access_token = os.environ.get("ACCESS_TOKEN")
    if not access_token:
        raise RuntimeError("GOOGLE_CALENDAR_TOKEN environment variable not set.")
    
    # Convert datetime objects to ISO format strings if needed
    if isinstance(start_time, datetime):
        start_time = start_time.isoformat()
    if isinstance(end_time, datetime):
        end_time = end_time.isoformat()
    
    # Construct the event
    event = {
        "summary": summary,
        "start": {
            "dateTime": start_time,
            "timeZone": timezone,
        },
        "end": {
            "dateTime": end_time,
            "timeZone": timezone,
        }
    }
    
    # Add optional fields if provided
    if description:
        event["description"] = description
    if location:
        event["location"] = location
    if attendees:
        event["attendees"] = attendees
    if recurrence:
        event["recurrence"] = recurrence
    
    # Make the API request
    url = f"https://www.googleapis.com/calendar/v3/calendars/{calendar_id}/events"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    params = {
        "sendNotifications": "true" if send_notifications else "false"
    }
    
    response = requests.post(url, headers=headers, json=event, params=params)
    response.raise_for_status()
    
    print(f"Event created: {response.json().get('htmlLink')}")
    return response.json()


# Example usage:
if __name__ == "__main__":
    # Get free slots
    free_slots = get_free_slots(time_min="2025-04-28T00:00:00.000+00:00", time_max="2025-04-28T23:59:00.000+00:00")
    
    # Print the results
    print(json.dumps(free_slots, indent=2))
    
    """
    # Example of creating a calendar event
    event = create_calendar_event(
        summary="Team Meeting VIP VIP VIP",
        start_time="2025-04-28T10:00:00-07:00",
        end_time="2025-04-28T11:00:00-07:00",
        description="Discuss project roadmap",
        location="Conference Room A",
        attendees=[
            {"email": "colleague1@example.com"},
            {"email": "colleague2@example.com"}
        ],
        recurrence=["RRULE:FREQ=WEEKLY;COUNT=4"]
    )
    print(json.dumps(event, indent=2))
    """