from urllib.parse import quote_plus

PLATFORM_BASES = {
    "Amazon": "https://www.amazon.in/s?k=",
    "Flipkart": "https://www.flipkart.com/search?q=",
    "IKEA": "https://www.ikea.com/in/en/search/?q=",
    "Swiggy": "https://www.swiggy.com/search?query=",
    "Zomato": "https://www.zomato.com/search?q=",
    "OYO": "https://www.oyorooms.com/search?location=",
}

def platform_search_url(platform: str, query: str) -> str:
    return PLATFORM_BASES.get(platform, PLATFORM_BASES["Amazon"]) + quote_plus(query)

def normalize_items(items: list[dict], budget: int) -> list[dict]:
    clean = []
    for item in items:
        try: price = max(0, int(float(item.get("estimated_price", 0))))
        except (TypeError, ValueError): price = 0
        try: quantity = max(1, int(item.get("quantity", 1)))
        except (TypeError, ValueError): quantity = 1
        platform = str(item.get("platform") or "Amazon")
        if platform not in PLATFORM_BASES: platform = "Amazon"
        name = str(item.get("name") or "Budget-friendly option")[:120]
        category = str(item.get("category") or "General")[:80]
        reason = str(item.get("reason") or "Selected to match the requested budget and preferences.")[:500]
        clean.append({"category": category, "name": name, "estimated_price": price, "quantity": quantity,
                      "platform": platform, "search_url": platform_search_url(platform, name), "reason": reason,
                      "budget_share": min(price * quantity, budget)})
    total = sum(x["estimated_price"] * x["quantity"] for x in clean)
    if total > budget and clean:
        scale = budget / total
        for x in clean:
            x["estimated_price"] = int(x["estimated_price"] * scale)
            x["budget_share"] = x["estimated_price"] * x["quantity"]
    return clean

def fallback_home(data: dict) -> dict:
    budget = int(data["budget"])
    items = [
        {"category":"Lighting","name":"LED ceiling light","estimated_price":max(1200,int(budget*.10)),"quantity":2,"platform":"IKEA","reason":"Useful lighting for the selected rooms."},
        {"category":"Furniture","name":"Compact storage cabinet","estimated_price":max(2500,int(budget*.20)),"quantity":1,"platform":"Amazon","reason":"Adds practical storage without using a large part of the budget."},
        {"category":"Decor","name":f'{data["style"].title()} wall decor set',"estimated_price":max(1500,int(budget*.12)),"quantity":1,"platform":"Flipkart","reason":"Matches the requested style while keeping the estimate moderate."},
    ]
    items=normalize_items(items,budget); total=sum(x["estimated_price"]*x["quantity"] for x in items)
    return {"planner":"home","budget":budget,"allocated_total":min(total,budget),"remaining":max(0,budget-total),
            "summary":"A practical home setup prioritizing lighting, storage, and decor.",
            "tips":["Measure room dimensions before buying large furniture.","Keep a small reserve for delivery and installation.","Verify current price and availability before purchase."],"items":items}

def fallback_party(data: dict) -> dict:
    budget=int(data["budget"]); guests=int(data["guest_count"])
    items=[
        {"category":"Food","name":f"Catering plan for {guests} guests","estimated_price":int(budget*.55),"quantity":1,"platform":"Swiggy","reason":"Food receives the largest allocation because it scales with guest count."},
        {"category":"Decoration","name":f'{data["event_type"].title()} decoration package',"estimated_price":int(budget*.20),"quantity":1,"platform":"Amazon","reason":"A moderate decoration allocation leaves room for food and contingency."},
        {"category":"Venue","name":f'{data["venue_type"].title()} event venue',"estimated_price":int(budget*.15),"quantity":1,"platform":"OYO","reason":"Venue suggestion for the selected event."},
    ]
    items=normalize_items(items,budget); total=sum(x["estimated_price"]*x["quantity"] for x in items)
    return {"planner":"party","budget":budget,"allocated_total":min(total,budget),"remaining":max(0,budget-total),
            "summary":f"A balanced {data['event_type']} plan for {guests} guests.",
            "tips":["Confirm venue capacity before paying a deposit.","Ask food vendors for per-person pricing and inclusions.","Keep a contingency amount for last-minute changes."],"items":items}

def fallback_jewelry(data: dict) -> dict:
    budget=int(data["budget"]); style=data.get("style","classic"); occasion=data.get("occasion","special occasion")
    items=[
        {"category":"Earrings","name":f"{style.title()} earrings for {occasion}","estimated_price":int(budget*.30),"quantity":1,"platform":"Amazon","reason":"A versatile accessory that can coordinate with the outfit style."},
        {"category":"Necklace","name":f"{style.title()} necklace set","estimated_price":int(budget*.40),"quantity":1,"platform":"Flipkart","reason":"Provides a focal accessory while remaining within the requested budget."},
    ]
    items=normalize_items(items,budget); total=sum(x["estimated_price"]*x["quantity"] for x in items)
    return {"planner":"jewelry","budget":budget,"allocated_total":min(total,budget),"remaining":max(0,budget-total),
            "summary":f"Jewelry suggestions for a {occasion} occasion with a {style} preference.",
            "tips":["Check material, size, seller, and return policy before purchase.","Use an outfit image only as a style reference.","Verify current marketplace price before buying."],"items":items}
