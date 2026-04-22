import ollama
import json
from router_agent.settings import SYSTEM_PROMPT, MODEL

# Intent classifier -> 'calendar' or 'general'
def detect_intent(user_message: str, model: str = MODEL) -> str:
    response = ollama.chat(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": user_message}
        ]
    )
    
    print("Detecting Intent of the message..")

    raw = response["message"]["content"].strip()

    try:
        parsed = json.loads(raw)
        intent = parsed.get("intent", "general")
        if intent not in ("calendar", "general"):
            return "general"  # safe fallback
        return intent
    except json.JSONDecodeError:
        # If the model misbehaves and returns text instead of JSON
        if "calendar" in raw.lower():
            return "calendar"
        return "general"



if __name__ == "__main__":
    test_messages = [
        "Schedule a meeting with John tomorrow at 3pm",
        "What is the capital of France?",
        "Am I free on Friday afternoon?",
        "Explain how black holes work",
        "Cancel my 10am appointment",
    ]

    for msg in test_messages:
        intent = detect_intent(msg)
        print(f"[{intent.upper()}] {msg}")