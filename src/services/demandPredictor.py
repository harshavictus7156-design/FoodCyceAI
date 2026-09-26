def forecast_summary(items):
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
