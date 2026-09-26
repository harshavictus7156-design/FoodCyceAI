import json
import os
import time
from typing import Any, Dict, List

DATA_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "mock_data.json")

DEFAULT_INVENTORY = [
    {
        "id": "item_1",
        "item": "Cooked Basmati Rice",
        "category": "Staples",
        "quantity_kg": 28.0,
        "expiry_hours": 6,
        "status": "Near Expiry",
        "prepared_time": "Today, 11:30 AM",
        "location": "Central Kitchen Hub, Bay 1",
        "storage_condition": "Hot insulated (>65°C)",
        "contact": "Chef Marcus (+91 98765 43210)",
    },
    {
        "id": "item_2",
        "item": "Garden Fresh Salad Mix",
        "category": "Vegetables",
        "quantity_kg": 16.0,
        "expiry_hours": 5,
        "status": "Near Expiry",
        "prepared_time": "Today, 10:45 AM",
        "location": "Cold Prep Station B",
        "storage_condition": "Chilled (4°C)",
        "contact": "Chef Sarah (+91 98765 43211)",
    },
    {
        "id": "item_3",
        "item": "Seasonal Fruit Platter",
        "category": "Fruit",
        "quantity_kg": 20.0,
        "expiry_hours": 18,
        "status": "Good",
        "prepared_time": "Today, 09:00 AM",
        "location": "Storage Unit 4",
        "storage_condition": "Chilled / Packaged",
        "contact": "Kitchen Store (+91 98765 43212)",
    },
    {
        "id": "item_4",
        "item": "Vegetable Lentil Soup",
        "category": "Prepared Food",
        "quantity_kg": 12.0,
        "expiry_hours": 3,
        "status": "Expired",
        "prepared_time": "Yesterday, 07:00 PM",
        "location": "Compost / Recovery Bin",
        "storage_condition": "Sealed container",
        "contact": "Kitchen Duty (+91 98765 43210)",
    },
    {
        "id": "item_5",
        "item": "Artisan Bread Loaves",
        "category": "Staples",
        "quantity_kg": 14.5,
        "expiry_hours": 24,
        "status": "Good",
        "prepared_time": "Today, 06:30 AM",
        "location": "Bakery Rack 2",
        "storage_condition": "Ambient / Dry",
        "contact": "Baker John (+91 98765 43213)",
    },
]

DEFAULT_STATE = {
    "registered_users": {
        "demo@foodcycle.ai": {
            "name": "Demo User",
            "email": "demo@foodcycle.ai",
            "password": "demo123",
            "role": "Kitchen Staff",
        }
    },
    "inventory": DEFAULT_INVENTORY,
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
    "kitchen_plan": {
        "day": "Monday",
        "meal_type": "Lunch",
        "plates": 400,
        "prepared_kg": 180.0,
        "predicted_surplus_plates": 44,
        "predicted_surplus_kg": 19.8,
        "waste_risk_kg": 19.8,
    },
}


def normalize_inventory_item(item: Dict[str, Any]) -> Dict[str, Any]:
    """Ensures an inventory item has all necessary keys to avoid KeyError in pandas or UI."""
    return {
        "id": str(item.get("id") or f"item_{int(time.time() * 1000)}"),
        "item": str(item.get("item") or "Food Item"),
        "category": str(item.get("category") or "Prepared Food"),
        "quantity_kg": float(item.get("quantity_kg", 10.0)),
        "expiry_hours": int(item.get("expiry_hours", 8)),
        "status": str(item.get("status") or "Good"),
        "prepared_time": str(item.get("prepared_time") or "Today, 11:30 AM"),
        "location": str(item.get("location") or "Main Kitchen Central Station"),
        "storage_condition": str(item.get("storage_condition") or "Chilled (4°C)"),
        "contact": str(item.get("contact") or "Kitchen Duty Manager (+91 98765 43210)"),
    }


def load_initial_data() -> Dict[str, Any]:
    """Loads seed data from mock_data.json with fallback to default state."""
    data = DEFAULT_STATE.copy()
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content:
                    loaded = json.loads(content)
                    if isinstance(loaded, dict):
                        data.update(loaded)
        except Exception:
            pass

    # Normalize all inventory items
    raw_inv = data.get("inventory", [])
    if isinstance(raw_inv, list):
        data["inventory"] = [normalize_inventory_item(item) for item in raw_inv if isinstance(item, dict)]
    else:
        data["inventory"] = [normalize_inventory_item(it) for it in DEFAULT_INVENTORY]

    return data


def save_current_data(
    inventory: List[Dict[str, Any]] = None,
    ngos: List[Dict[str, Any]] = None,
    tasks: List[Dict[str, Any]] = None,
    registered_users: Dict[str, Any] = None,
    kitchen_plan: Dict[str, Any] = None,
) -> bool:
    """Saves active state to mock_data.json with complete schemas."""
    try:
        data = load_initial_data()
        if inventory is not None:
            data["inventory"] = [normalize_inventory_item(it) for it in inventory]
        if ngos is not None:
            data["ngos"] = ngos
        if tasks is not None:
            data["tasks"] = tasks
        if registered_users is not None:
            data["registered_users"] = registered_users
        if kitchen_plan is not None:
            data["kitchen_plan"] = kitchen_plan

        os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return True
    except Exception:
        return False
