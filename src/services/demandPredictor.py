from typing import Any, Dict, List


def forecast_summary(items: List[Dict[str, Any]]) -> Dict[str, Any]:
    total_prepared = sum(float(item.get("quantity_kg", 0)) for item in items)
    surplus = sum(
        float(item.get("quantity_kg", 0))
        for item in items
        if item.get("status") in ["Near Expiry", "Expired", "Dispatched"]
    )
    donated = min(int(total_prepared * 0.6), 500)
    waste_saved = max(0, int(total_prepared * 0.22))
    return {
        "prepared": round(total_prepared, 1),
        "surplus": round(surplus, 1),
        "donated": donated,
        "waste_saved": waste_saved,
        "expected_demand": 520,
    }


def predict_kitchen_waste(day: str, meal_type: str, plates: int) -> Dict[str, Any]:
    """Predicts surplus food and waste risks based on kitchen plate counts and operational parameters."""
    day_factors = {
        "Monday": 0.11,
        "Tuesday": 0.08,
        "Wednesday": 0.08,
        "Thursday": 0.09,
        "Friday": 0.12,
        "Saturday": 0.14,
        "Sunday": 0.15,
    }
    meal_multipliers = {
        "Breakfast": 0.85,
        "Lunch": 1.0,
        "Dinner": 1.15,
        "Event catering": 1.35,
    }

    base_rate = day_factors.get(day, 0.10)
    multiplier = meal_multipliers.get(meal_type, 1.0)
    surplus_rate = min(0.30, max(0.05, base_rate * multiplier))

    plate_weight_kg = 0.45  # standard meal portion
    total_prepared_kg = round(plates * plate_weight_kg, 1)

    predicted_surplus_plates = int(round(plates * surplus_rate))
    predicted_surplus_kg = round(predicted_surplus_plates * plate_weight_kg, 1)
    safe_consumption_plates = plates - predicted_surplus_plates

    return {
        "day": day,
        "meal_type": meal_type,
        "plates": plates,
        "total_prepared_kg": total_prepared_kg,
        "surplus_rate_pct": round(surplus_rate * 100, 1),
        "predicted_surplus_plates": predicted_surplus_plates,
        "predicted_surplus_kg": predicted_surplus_kg,
        "safe_consumption_plates": safe_consumption_plates,
        "co2_avoidable_kg": round(predicted_surplus_kg * 1.45, 1),
        "water_avoidable_liters": int(predicted_surplus_kg * 18),
    }
