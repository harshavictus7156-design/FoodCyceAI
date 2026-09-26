import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.services.dataService import load_initial_data, save_current_data
from src.services.demandPredictor import forecast_summary
from src.services.geminiService import heuristic_analysis
from src.services.logisticsService import (
    claim_food_for_partner,
    complete_or_reset_partner,
    connect_partner,
)
from src.utils.esgCalculator import calculate_esg_metrics
from app import compute_inventory_status


def test_inventory_status():
    assert compute_inventory_status(2) == "Expired"
    assert compute_inventory_status(4) == "Expired"
    assert compute_inventory_status(5) == "Near Expiry"
    assert compute_inventory_status(10) == "Near Expiry"
    assert compute_inventory_status(12) == "Good"
    print("test_inventory_status passed!")


def test_forecast_summary():
    items = [
        {"item": "Rice", "quantity_kg": 20.0, "status": "Good"},
        {"item": "Salad", "quantity_kg": 10.0, "status": "Near Expiry"},
        {"item": "Soup", "quantity_kg": 5.0, "status": "Expired"},
    ]
    summary = forecast_summary(items)
    assert summary["prepared"] == 35.0
    assert summary["surplus"] == 15.0
    assert summary["donated"] > 0
    assert summary["waste_saved"] > 0
    print("test_forecast_summary passed!")


def test_esg_calculator():
    items = [
        {"item": "Rice", "quantity_kg": 50.0, "status": "Good"},
    ]
    metrics = calculate_esg_metrics(items)
    assert metrics["carbon_saved"] > 0
    assert metrics["water_saved"] > 0
    assert 0 <= metrics["esg_score"] <= 100
    print("test_esg_calculator passed!")


def test_logistics():
    inventory = [
        {"id": "item_1", "item": "Rice", "quantity_kg": 20.0, "status": "Near Expiry"},
        {"id": "item_2", "item": "Salad", "quantity_kg": 10.0, "status": "Good"},
    ]
    ngo = {"name": "Test NGO", "distance_km": 3.0, "status": "Available"}
    tasks = []

    # Connect partner
    ok, msg = connect_partner(ngo, inventory, tasks)
    assert ok is True
    assert ngo["status"] == "Connected"
    assert inventory[0]["status"] == "Dispatched"
    assert len(tasks) == 1
    assert tasks[0]["status"] == "In Transit"

    # Reset / Complete partner
    ok, msg = complete_or_reset_partner(ngo, tasks)
    assert ok is True
    assert ngo["status"] == "Available"
    assert tasks[0]["status"] == "Delivered"

    # Claim food
    ok, msg = claim_food_for_partner(ngo, inventory, tasks)
    assert ok is True
    assert ngo["status"] == "Claimed"
    assert inventory[1]["status"] == "Dispatched"
    print("test_logistics passed!")


def test_heuristic_analysis():
    fresh_res = heuristic_analysis("Freshly cooked warm rice, stored in clean container")
    assert fresh_res["status"] == "Good"
    assert fresh_res["freshness_percent"] > 80

    spoiled_res = heuristic_analysis("Spoiled rotten soup with mold and foul smell")
    assert spoiled_res["status"] == "Expired"
    assert spoiled_res["freshness_percent"] < 40
    print("test_heuristic_analysis passed!")


def test_data_service():
    data = load_initial_data()
    assert "registered_users" in data
    assert "inventory" in data
    assert "ngos" in data
    assert "tasks" in data
    print("test_data_service passed!")


if __name__ == "__main__":
    test_inventory_status()
    test_forecast_summary()
    test_esg_calculator()
    test_logistics()
    test_heuristic_analysis()
    test_data_service()
    print("\nALL BACKEND UNIT TESTS PASSED SUCCESSFULLY!")
