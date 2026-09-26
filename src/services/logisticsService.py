from typing import Any, Dict, List, Tuple
from src.services.dataService import save_current_data


def connect_partner(
    ngo: Dict[str, Any], inventory: List[Dict[str, Any]], tasks: List[Dict[str, Any]]
) -> Tuple[bool, str]:
    if not inventory:
        return False, "No food items available to dispatch."

    if ngo.get("status") in ["Connected", "In Transit"]:
        return False, f"{ngo['name']} is already connected to an active delivery route."

    # Prioritize Near Expiry items first to prevent waste, then Good items
    item = next((entry for entry in inventory if entry.get("status") == "Near Expiry"), None)
    if item is None:
        item = next((entry for entry in inventory if entry.get("status") == "Good"), None)
    if item is None:
        item = next((entry for entry in inventory if entry.get("status") not in ["Dispatched", "Expired"]), None)

    if item is None:
        return False, "All available items are already dispatched or expired."

    item["status"] = "Dispatched"
    ngo["status"] = "Connected"
    tasks.append(
        {
            "task": f"{item['item']} dispatch",
            "recipient": ngo["name"],
            "status": "In Transit",
            "eta": f"{max(15, int(ngo.get('distance_km', 5) * 4))} min",
            "location": item.get("location", "Main Kitchen Hub"),
            "contact": item.get("contact", "Kitchen Staff"),
        }
    )
    save_current_data(inventory=inventory, tasks=tasks)
    return True, f"Connected {ngo['name']} to {item['item']} ({item.get('quantity_kg', 0)} kg)."


def claim_food_for_partner(
    ngo: Dict[str, Any], inventory: List[Dict[str, Any]], tasks: List[Dict[str, Any]]
) -> Tuple[bool, str]:
    if not inventory:
        return False, "No inventory available for claim."

    if ngo.get("status") == "Claimed":
        return False, f"{ngo['name']} has already claimed an active allocation."

    item = next((entry for entry in inventory if entry.get("status") == "Near Expiry"), None)
    if item is None:
        item = next((entry for entry in inventory if entry.get("status") == "Good"), None)
    if item is None:
        return False, "No eligible surplus food item can be claimed right now."

    item["status"] = "Dispatched"
    ngo["status"] = "Claimed"
    tasks.append(
        {
            "task": f"{item['item']} claim allocation",
            "recipient": ngo["name"],
            "status": "Claimed",
            "eta": f"{max(10, int(ngo.get('distance_km', 4) * 3))} min",
            "location": item.get("location", "Main Kitchen Hub"),
            "contact": item.get("contact", "Kitchen Staff"),
        }
    )
    save_current_data(inventory=inventory, tasks=tasks)
    return True, f"{ngo['name']} claimed {item['item']} ({item.get('quantity_kg', 0)} kg) successfully."


def claim_specific_food_item(
    ngo: Dict[str, Any], item_id: str, inventory: List[Dict[str, Any]], tasks: List[Dict[str, Any]]
) -> Tuple[bool, str]:
    """Allows an NGO to claim a specific posted surplus batch."""
    item = next((entry for entry in inventory if entry.get("id") == item_id), None)
    if not item:
        return False, "Selected surplus food batch was not found."
    if item.get("status") in ["Dispatched", "Claimed", "Expired"]:
        return False, f"{item['item']} is already {item.get('status')}."

    item["status"] = "Claimed"
    ngo["status"] = "Claimed"
    tasks.append(
        {
            "task": f"{item['item']} pickup ({item.get('quantity_kg', 0)} kg)",
            "recipient": ngo["name"],
            "status": "Claimed",
            "eta": f"{max(10, int(ngo.get('distance_km', 4) * 3))} min",
            "location": item.get("location", "Kitchen Dispatch Station"),
            "contact": item.get("contact", "Kitchen Duty Manager"),
        }
    )
    save_current_data(inventory=inventory, tasks=tasks)
    return True, f"{ngo['name']} successfully claimed {item['item']} ({item.get('quantity_kg', 0)} kg)!"


def complete_or_reset_partner(
    ngo: Dict[str, Any], tasks: List[Dict[str, Any]]
) -> Tuple[bool, str]:
    """Marks existing partner tasks as Completed and resets status to Available."""
    ngo["status"] = "Available"
    for t in tasks:
        if t.get("recipient") == ngo.get("name") and t.get("status") in ["In Transit", "Assigned", "Claimed"]:
            t["status"] = "Delivered"
            t["eta"] = "Done"
    save_current_data(tasks=tasks)
    return True, f"Completed dispatch for {ngo['name']}. Partner is now Available."
