"""Application configuration and constants for FoodCycle AI."""

APP_NAME = "FoodCycle AI"
APP_TAGLINE = "Zero-waste food redistribution and quality management"
APP_VERSION = "2.1.0"

# Category choices
FOOD_CATEGORIES = [
    "Staples",
    "Vegetables",
    "Fruit",
    "Prepared Food",
    "Dairy",
    "Bakery",
    "Beverages",
]

# Expiry thresholds in hours
EXPIRED_THRESHOLD_HOURS = 4
NEAR_EXPIRY_THRESHOLD_HOURS = 10

# Partner types
PARTNER_TYPES = [
    "Community Hub",
    "Large Distribution",
    "Support Network",
    "Local Service",
]
