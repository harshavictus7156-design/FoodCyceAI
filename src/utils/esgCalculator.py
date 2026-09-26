def calculate_esg_metrics(inventory):
    total_kg = sum(float(item.get("quantity_kg", 0)) for item in inventory)
    carbon_saved = round(total_kg * 1.45, 1)
    water_saved = int(total_kg * 18)
    food_recovery = min(96, int((total_kg / max(1, total_kg + 45)) * 100))
    score = min(98, max(55, 68 + food_recovery // 2))
    return {
        "total_kg": round(total_kg, 1),
        "carbon_saved": carbon_saved,
        "water_saved": water_saved,
        "food_recovery": food_recovery,
        "esg_score": score,
    }
