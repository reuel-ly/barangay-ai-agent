import ollama
import json
import datetime
from calendar_agent.google_calendar import check_day_availability, create_calendar_event
from calendar_agent.settings import MODEL

# -------------------------------------------------------
# Step 1: Model only extracts parameters (simple task)
# -------------------------------------------------------
def extract_calendar_params(question: str) -> dict:
    """
    Ask the model to extract date, time, title from the user message.
    This is a single step — no tool calling needed.
    """
    today = datetime.date.today().isoformat()
    prompt = f"""
Today is {today}.
Extract scheduling information from the user message below.

Return ONLY a JSON object with these fields:
- "action": one of "check" or "create"
- "date": the date in YYYY-MM-DD format (convert relative dates like 'tomorrow', 'next Monday')
- "title": event title if creating, null if just checking
- "start_time": in HH:MM 24hr format, null if not mentioned
- "end_time": in HH:MM 24hr format, null if not mentioned (assume 1hr after start if not given)
- "description": optional description, null if not mentioned

User message: "{question}"

JSON only. No explanation.
"""
    

    response = ollama.chat(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}]
    )

    raw = response.message.content.strip()

    # Clean markdown fences if model adds them
    raw = raw.replace("```json", "").replace("```", "").strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # Fallback: assume check availability for today
        return {"action": "check", "date": today, "title": None, "start_time": None, "end_time": None, "description": None}



def run_calendar_logic(params: dict) -> dict:
    """
    Pure Python logic
    """
    date = params.get("date")
    action = params.get("action", "check")

    
    availability = check_day_availability(date)
    print(f"[Calendar Logic] Availability for {date}: {availability}")

    if not availability["available"]:
        return {
            "success": False,
            "reason": "busy",
            "events": availability["events"],
            "date": date,
            "message": availability["message"]
        }

    # Day is free — create if requested
    if action == "create":
        title      = params.get("title") or "New Event"
        start_time = params.get("start_time") or "09:00"

        # Calculate end_time if not given
        if params.get("end_time"):
            end_time = params["end_time"]
        else:
            # Add 1 hour to start_time
            start_dt = datetime.datetime.strptime(start_time, "%H:%M")
            end_time = (start_dt + datetime.timedelta(hours=1)).strftime("%H:%M")

        result = create_calendar_event(
            title=title,
            date_str=date,
            start_time=start_time,
            end_time=end_time,
            description=params.get("description") or ""
        )
        print(f"[Calendar Logic] Event created: {result}")
        return {
            "success": True,
            "reason": "created",
            "date": date,
            "title": title,
            "start_time": start_time,
            "end_time": end_time,
            "message": result["message"]
        }

    # Just checking availability
    return {
        "success": True,
        "reason": "free",
        "date": date,
        "message": f"You are free on {date}."
    }


# -------------------------------------------------------
# Step 3: Model generates a friendly response (simple task)
def generate_response(question: str, result: dict) -> str:
    """
    Give the model the result and ask it to respond naturally.
    Single step — just formatting, no reasoning needed.
    """
    prompt = f"""
The user asked: "{question}"

Here is the result from the calendar system:
{json.dumps(result, indent=2)}

Write a short, friendly response to the user based on this result.
- If busy: mention the existing events and suggest picking another day
- If created: confirm the event details clearly
- If free: let them know the day is open
Do not make up any information. Only use what is in the result.
"""

    response = ollama.chat(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}]
    )

    return response.message.content.strip()



async def handle_calendar(question: str, history: list) -> dict:
    print(f"\n{'='*50}")
    print(f"📅 [CALENDAR AGENT] Question: {question}")

    # Step 1: Extract parameters
    params = extract_calendar_params(question)
    print(f"📌 [EXTRACTED PARAMS] {params}")

    # Step 2: Run logic in Python
    result = run_calendar_logic(params)
    print(f"📊 [LOGIC RESULT] {result}")

    # Step 3: Generate friendly response
    response_text = generate_response(question, result)
    print(f"💬 [FINAL RESPONSE] {response_text}")
    print(f"{'='*50}\n")

    return {
        "answer": response_text,
        "sources": [],
        "retrieved_texts": [],
        "intent": "calendar"
    }