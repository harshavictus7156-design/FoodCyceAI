# 🌱 FoodCycle AI — Food Recovery & Quality Platform

FoodCycle AI is a production-ready food recovery and redistribution platform designed to bridge the gap between commercial kitchens, food safety inspectors, and charitable organizations (NGOs, shelters, and food banks) to prevent food waste in real time.

---

## 🌟 Key Features

1. **AI Freshness & Shelf-Life Inspector**:
   - Inspect food items via image upload or sensory/storage condition descriptions.
   - Powered by Gemini Vision API with a fallback heuristic engine.
   - Direct 1-click addition of inspected items to the live recovery inventory.

2. **Real-time Live Inventory Management**:
   - Automatic status classification (`Good`, `Near Expiry`, `Expired`) based on remaining shelf-life hours.
   - Batch entry, live cards, and deletion by unique item ID.
   - Persistent synchronization with backend data storage.

3. **Intelligent NGO Logistics & Route Matching**:
   - Matches near-expiry surplus food with nearby vetted partners and shelters.
   - Real-time status progression (`Available` ➔ `Connected` / `Claimed` ➔ `Delivered`).
   - Active route tracking table with ETA calculation and geographic map overview.

4. **ESG Sustainability & Carbon Accounting**:
   - Live metrics: Carbon avoided (kg CO2), water conserved (Liters), recovery rate (%), and composite ESG Score.
   - Interactive Plotly visualizations for surplus trends and footprint allocation.
   - Exportable official audited ESG Compliance Report in CSV format.

5. **Authentication & Session Flow**:
   - Role-based profiles: Kitchen Staff, NGO Partner, Food Inspector, Sustainability Manager.
   - Secure login, user registration, and 1-Click Demo login.
   - Persistent session state across all pages and actions.

---

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.10+
- Virtual environment installed

### 2. Run the App
```bash
# Activate your virtual environment
.\animalprevention.venv\Scripts\activate

# Launch the Streamlit application
streamlit run app.py
```

### 3. Demo Credentials
- **Email:** `demo@foodcycle.ai`
- **Password:** `demo123`
- *Alternatively, click the **⚡ 1-Click Demo Login** or **Explore as Guest** button.*

---

## 🧪 Running Tests
To validate all backend services, algorithms, and data persistence:
```bash
.\animalprevention.venv\Scripts\python scripts/test_backend.py
```

---

## 📁 Project Structure
```
├── app.py                      # Main Streamlit web application & UI
├── .streamlit/
│   └── config.toml             # Theme configuration enforcing clean light theme
├── config/
│   └── settings.py             # Global constants, thresholds, and categories
├── data/
│   └── mock_data.json          # Persistent JSON storage for inventory & state
├── scripts/
│   └── test_backend.py         # Automated test suite for backend services
├── src/
│   ├── services/
│   │   ├── dataService.py      # State persistence & sync engine
│   │   ├── demandPredictor.py  # Kitchen surplus & demand forecasting
│   │   ├── geminiService.py    # Gemini vision & heuristic inspection
│   │   └── logisticsService.py # NGO matching, dispatch & lifecycle logic
│   └── utils/
│       └── esgCalculator.py    # ESG score, water & carbon savings formulas
└── requirements.txt            # Python dependencies
```

---

## 🌿 Clean UI & High-Contrast Design
- **Theme:** Forced Light theme with `#F8F9FA` off-white canvas and `#FFFFFF` cards.
- **Typography:** Inter font family with crisp dark headings (`#0F172A`) and visible form labels.
- **Accents:** Emerald green (`#10B981`) primary buttons and status indicators.
- **Input Visibility:** Solid white input fields with explicit `#CBD5E1` borders and `#94A3B8` placeholders.
