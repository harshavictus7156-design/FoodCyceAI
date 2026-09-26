import json
import os
from typing import Any, Dict, Optional

try:
    from google import genai
    from google.genai import types
except Exception:  # pragma: no cover
    genai = None
    types = None


def get_api_key() -> str:
    key = os.getenv("GEMINI_API_KEY")
    if key:
        return key
    try:
        import streamlit as st

        return str(st.secrets.get("GEMINI_API_KEY", ""))
    except Exception:
        return ""


def safe_json_object(raw: Any) -> Dict[str, Any]:
    if not raw:
        return {}
    text = str(raw).strip()
    if text.startswith("```"):
        text = text.replace("```json", "").replace("```", "").strip()
    if text.lower().startswith("json"):
        text = text[4:].strip()
    try:
        return json.loads(text)
    except Exception:
        return {}


def heuristic_analysis(description: str = "") -> Dict[str, Any]:
    text = (description or "").lower()
    if any(word in text for word in ["spoiled", "rotten", "mold", "expired", "off smell", "oxidized", "unsafe"]):
        return {
            "freshness_percent": 26,
            "expiry_prediction": "2 hours",
            "status": "Expired",
            "consumption_recommendation": "Discard immediately and route for composting or anaerobic digestion.",
        }

    if any(word in text for word in ["fresh", "clean", "recently cooked", "cold stored", "properly sealed", "safe", "normal"]):
        return {
            "freshness_percent": 92,
            "expiry_prediction": "18 hours",
            "status": "Good",
            "consumption_recommendation": "Redistribute within the next 12 hours while the cold chain remains stable.",
        }

    if any(word in text for word in ["warm", "stale", "near expiry", "day old", "left out", "aging"]):
        return {
            "freshness_percent": 61,
            "expiry_prediction": "7 hours",
            "status": "Near Expiry",
            "consumption_recommendation": "Prioritize rapid redistribution to the nearest partner before expiry.",
        }

    return {
        "freshness_percent": 74,
        "expiry_prediction": "10 hours",
        "status": "Near Expiry",
        "consumption_recommendation": "Review storage conditions and redispatch quickly to avoid waste.",
    }


def analyze_food_quality(uploaded_file=None, description: str = "") -> Dict[str, Any]:
    if uploaded_file is None:
        return heuristic_analysis(description)

    api_key = get_api_key()
    if not api_key or genai is None or types is None:
        return heuristic_analysis(description)

    try:
        image_bytes = uploaded_file.getvalue()
        mime_type = getattr(uploaded_file, "type", "") or "image/png"
        client = genai.Client(api_key=api_key)
        prompt = (
            "Inspect the uploaded food image and return ONLY valid JSON with keys "
            "freshness_percent, expiry_prediction, status, consumption_recommendation. "
            "Status must be Good, Near Expiry, or Expired. "
            f"Description: {description or 'No description provided.'}"
        )

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                types.Part.from_text(prompt),
                types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
            ],
        )

        raw_text = getattr(response, "text", "") or ""
        if not raw_text:
            for part in getattr(response, "candidates", []) or []:
                content = getattr(part, "content", None)
                if content:
                    for p in getattr(content, "parts", []) or []:
                        text = getattr(p, "text", "") or ""
                        if text:
                            raw_text = text
                            break
                    if raw_text:
                        break

        payload = safe_json_object(raw_text)
        if payload:
            return {
                "freshness_percent": int(payload.get("freshness_percent", 80)),
                "expiry_prediction": payload.get("expiry_prediction", "12 hours"),
                "status": payload.get("status", "Good"),
                "consumption_recommendation": payload.get(
                    "consumption_recommendation",
                    "Redistribute to the nearest safe channel as soon as possible.",
                ),
            }
    except Exception:
        pass

    return heuristic_analysis(description)
