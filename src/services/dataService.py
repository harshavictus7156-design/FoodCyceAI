import json
import os
from typing import Any, Dict

DATA_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "mock_data.json")

DEFAULT_STATE = {
    "registered_users": {
        "demo@foodcycle.ai": {
            "name": "Demo User",
            "email": "demo@foodcycle.ai",
            "password": "demo123",
            "role": "Kitchen Staff",
        }
    },
    "inventory": [
        {"id": "item_1", "item": "Cooked Basmati Rice", "quantity_kg": 28.0, "expiry_hours": 6, "status": "Near Expiry", "category": "Staples"},
        {"id": "item_2", "item": "Garden Fresh Salad Mix", "quantity_kg": 16.0, "expiry_hours": 5, "status": "Near Expiry", "category": "Vegetables"},
        {"id": "item_3", "item": "Seasonal Fruit Platter", "quantity_kg": 20.0, "expiry_hours": 18, "status": "Good", "category": "Fruit"},
        {"id": "item_4", "item": "Vegetable Lentil Soup", "quantity_kg": 12.0, "expiry_hours": 3, "status": "Expired", "category": "Prepared Food"},
        {"id": "item_5", "item": "Artisan Bread Loaves", "quantity_kg": 14.5, "expiry_hours": 24, "status": "Good", "category": "Staples"},
    ],
    "ngos": [
        {"name": "Local NGOs Hub", "distance_km": 4.2, "capacity_kg": 100, "type": "Community Hub", "status": "Available"},
        {"name": "City Food Bank", "distance_km": 8.4, "capacity_kg": 180, "type": "Large Distribution", "status": "Available"},
        {"name": "Hope Shelter Network", "distance_km": 6.1, "capacity_kg": 130, "type": "Support Network", "status": "Available"},
        {"name": "Community Care Kitchen", "distance_km": 9.8, "capacity_kg": 160, "type": "Local Service", "status": "Available"},
    ],
    "tasks": [
        {"task": "Vegetable Lentil Soup dispatch", "recipient": "Local NGOs Hub", "status": "Assigned", "eta": "30 min"},
        {"task": "Garden Fresh Salad transfer", "recipient": "Hope Shelter Network", "status": "In Transit", "eta": "45 min"},
    ],
}


def load_initial_data() -> Dict[str, Any]:
    """Loads seed data from mock_data.json with fallback to default state."""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content:
                    return json.loads(content)
        except Exception:
            pass
    return DEFAULT_STATE.copy()


def save_current_data(inventory=None, ngos=None, tasks=None, registered_users=None) -> bool:
    """Saves the active application state to mock_data.json for persistence."""
    try:
        data = load_initial_data()
        if inventory is not None:
            data["inventory"] = inventory
        if ngos is not None:
            data["ngos"] = ngos
        if tasks is not None:
            data["tasks"] = tasks
        if registered_users is not None:
            data["registered_users"] = registered_users

        os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return True
    except Exception:
        return False
