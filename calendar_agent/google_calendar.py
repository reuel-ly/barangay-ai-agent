import os
import json
import datetime
from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

load_dotenv()

SCOPES = ["https://www.googleapis.com/auth/calendar"]

def get_calendar_service():
    creds = None

    # Load token if it exists
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Build the client config 
            client_config = {
                "installed": {
                    "client_id":     os.getenv("GOOGLE_CLIENT_ID"),
                    "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
                    "auth_uri":      os.getenv("GOOGLE_AUTH_URI"),
                    "token_uri":     os.getenv("GOOGLE_TOKEN_URI"),
                    "redirect_uris": [os.getenv("GOOGLE_REDIRECT_URI", "http://localhost")]
                }
            }

            flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
            creds = flow.run_local_server(
                port=8080,
                prompt="select_account consent",   # ← "consent" forces full account screen
                login_hint="yourpersonalgmail@gmail.com"  # ← put your personal email here
            )

        # Save the token for future runs
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return build("calendar", "v3", credentials=creds)



def check_day_availability(date_str: str) -> dict:
    service = get_calendar_service()
    start = f"{date_str}T00:00:00Z"
    end   = f"{date_str}T23:59:59Z"

    events_result = service.events().list(
        calendarId="primary",
        timeMin=start,
        timeMax=end,
        singleEvents=True,
        orderBy="startTime"
    ).execute()

    events = events_result.get("items", [])

    if not events:
        return {"available": True, "events": [], "message": f"No events on {date_str}."}

    event_list = [
        {"title": e.get("summary", "Untitled"), "start": e["start"].get("dateTime", e["start"].get("date"))}
        for e in events
    ]
    return {"available": False, "events": event_list, "message": f"Found {len(events)} event(s) on {date_str}."}


def create_calendar_event(title: str, date_str: str, start_time: str, end_time: str, description: str = "") -> dict:
    service = get_calendar_service()

    event = {
        "summary": title,
        "description": description,
        "start": {"dateTime": f"{date_str}T{start_time}:00", "timeZone": "Asia/Manila"},
        "end":   {"dateTime": f"{date_str}T{end_time}:00",   "timeZone": "Asia/Manila"},
    }

    created = service.events().insert(calendarId="primary", body=event).execute()
    return {
        "success": True,
        "event_id": created["id"],
        "link": created.get("htmlLink"),
        "message": f"Event '{title}' created on {date_str} from {start_time} to {end_time}."
    }