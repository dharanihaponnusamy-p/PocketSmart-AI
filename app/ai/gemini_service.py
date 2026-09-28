import json
from typing import Any
from google import genai
from google.genai import types
from ..config import settings
from ..services.planners import home_prompt, party_prompt, jewelry_prompt, fallback_for
from ..services.recommendations import normalize_items

class GeminiService:
    def __init__(self):
        self.enabled=bool(settings.gemini_api_key)
        self.client=genai.Client(api_key=settings.gemini_api_key) if self.enabled else None

    def _generate(self,prompt:str,image_bytes:bytes|None=None,mime_type:str|None=None):
        if not self.client: raise RuntimeError("Gemini API key is not configured")
        contents: list[Any]=[prompt]
        if image_bytes and mime_type:
            contents.append(types.Part.from_bytes(data=image_bytes,mime_type=mime_type))
        response=self.client.models.generate_content(
            model=settings.gemini_model, contents=contents,
            config=types.GenerateContentConfig(temperature=.4,response_mime_type="application/json"))
        text=getattr(response,"text",None)
        if not text: raise RuntimeError("Gemini returned an empty response")
        return json.loads(text)

    def recommend(self,planner,data,image_bytes=None,mime_type=None):
        prompt={"home":home_prompt,"party":party_prompt,"jewelry":lambda d:jewelry_prompt(d,bool(image_bytes))}[planner](data)
        try:
            raw=self._generate(prompt,image_bytes,mime_type)
            items=normalize_items(raw.get("items",[]),int(data["budget"]))
            if not items: raise ValueError("No usable recommendation items")
            total=sum(i["estimated_price"]*i["quantity"] for i in items)
            return ({"planner":planner,"budget":int(data["budget"]),"allocated_total":min(total,int(data["budget"])),
                     "remaining":max(0,int(data["budget"])-total),"summary":str(raw.get("summary") or "AI-generated budget recommendations."),
                     "tips":[str(x) for x in raw.get("tips",[])][:6],"items":items},True)
        except Exception:
            return fallback_for(planner,data),False

gemini_service=GeminiService()
