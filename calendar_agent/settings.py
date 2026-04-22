import datetime

MODEL='mistral:latest'

# Tool schemas for Mistral 
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "check_day_availability",
            "description": "Check if there are any existing events on a specific date before scheduling.",
            "parameters": {
                "type": "object",
                "properties": {
                    "date_str": {
                        "type": "string",
                        "description": "The date to check in YYYY-MM-DD format."
                    }
                },
                "required": ["date_str"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_calendar_event",
            "description": "Create a new event on Google Calendar. Only call this if check_day_availability confirms the day is free.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title":       {"type": "string", "description": "Title of the event."},
                    "date_str":    {"type": "string", "description": "Date in YYYY-MM-DD format."},
                    "start_time":  {"type": "string", "description": "Start time in HH:MM format (24hr)."},
                    "end_time":    {"type": "string", "description": "End time in HH:MM format (24hr)."},
                    "description": {"type": "string", "description": "Optional description of the event."}
                },
                "required": ["title", "date_str", "start_time", "end_time"]
            }
        }
    }
]
