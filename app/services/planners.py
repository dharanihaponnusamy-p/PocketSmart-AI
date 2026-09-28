import json

def home_prompt(data):
    return f'''You are PocketSmart AI, a budget planning assistant. Create practical home-interior recommendations.
Budget: INR {data["budget"]}
Rooms: {json.dumps(data["rooms"])}
Style: {data["style"]}
Notes: {data["notes"]}
Return ONLY JSON with keys summary, tips, items. Each item must contain category, name, estimated_price, quantity, platform, reason. Use INR integers, keep the total within budget, and do not claim live stock, ratings, or exact current prices.'''

def party_prompt(data):
    return f'''You are PocketSmart AI, a budget planning assistant. Plan a {data["event_type"]} for {data["guest_count"]} guests.
Budget: INR {data["budget"]}; Venue: {data["venue_type"]}; City: {data["city"]}; Notes: {data["notes"]}
Return ONLY JSON with keys summary, tips, items. Each item must contain category, name, estimated_price, quantity, platform, reason. Use INR integers, keep the total within budget, and do not claim live availability or exact vendor prices.'''

def jewelry_prompt(data, image_attached):
    image_note = "An outfit image is attached. Analyze general colors, neckline and style." if image_attached else "No outfit image is attached."
    return f'''You are PocketSmart AI, a style-aware jewelry budget planning assistant.
Budget: INR {data["budget"]}; Occasion: {data["occasion"]}; Style: {data["style"]}; Notes: {data["notes"]}
{image_note}
Return ONLY JSON with keys summary, tips, items. Each item must contain category, name, estimated_price, quantity, platform, reason. Use INR integers, keep the total within budget, and do not identify a person or claim live product availability.'''

def fallback_for(planner, data):
    from .recommendations import fallback_home, fallback_party, fallback_jewelry
    return {"home":fallback_home,"party":fallback_party,"jewelry":fallback_jewelry}[planner](data)
