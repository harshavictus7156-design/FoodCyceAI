import os
import time
from typing import Any, Dict, List

import pandas as pd
import plotly.express as px
import streamlit as st
from PIL import Image

from config.settings import FOOD_CATEGORIES
from src.services.dataService import load_initial_data, save_current_data, normalize_inventory_item
from src.services.demandPredictor import forecast_summary, predict_kitchen_waste
from src.services.geminiService import analyze_food_quality
from src.services.logisticsService import (
    claim_food_for_partner,
    claim_specific_food_item,
    complete_or_reset_partner,
    connect_partner,
)
from src.utils.esgCalculator import calculate_esg_metrics

st.set_page_config(page_title="FoodCycle AI", page_icon="🌱", layout="wide")

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

:root {
    --bg: #F8F9FA;
    --panel: #FFFFFF;
    --panel-soft: #F1F5F9;
    --line: #E2E8F0;
    --text: #0F172A;
    --text-muted: #475569;
    --green: #10B981;
    --green-deep: #059669;
    --green-soft: rgba(16,185,129,0.12);
    --amber: #F59E0B;
    --amber-soft: rgba(245,158,11,0.14);
    --red: #EF4444;
    --red-soft: rgba(239,68,68,0.12);
    --shadow: 0 10px 30px rgba(15, 23, 42, 0.08);
}

/* Force light theme container background and dark text */
html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'Inter', sans-serif;
}

[data-testid="stHeader"] {
    background: rgba(255,255,255,0.0);
    box-shadow: none;
}

.block-container {
    max-width: 1450px !important;
    padding-top: 1.2rem !important;
    padding-left: 1.4rem !important;
    padding-right: 1.4rem !important;
}

/* Universal text & heading contrast */
h1, h2, h3, h4, h5, h6 {
    color: #0F172A !important;
    font-weight: 800 !important;
}

p, span, div {
    color: #0F172A;
}

/* Explicit Form Labels - High Contrast & Visible */
label,
[data-testid="stWidgetLabel"],
[data-testid="stWidgetLabel"] p,
[data-testid="stWidgetLabel"] span {
    color: #0F172A !important;
    font-weight: 600 !important;
    font-size: 0.90rem !important;
    margin-bottom: 0.25rem !important;
}

/* BaseWeb Text Input, Select, and TextArea Fields */
div[data-baseweb="input"],
div[data-baseweb="base-input"] {
    background-color: #FFFFFF !important;
    border: 1.5px solid #CBD5E1 !important;
    border-radius: 12px !important;
    color: #0F172A !important;
    transition: all 0.2s ease;
}

div[data-baseweb="input"]:focus-within,
div[data-baseweb="base-input"]:focus-within {
    border-color: #10B981 !important;
    box-shadow: 0 0 0 3px rgba(16,185,129,0.18) !important;
}

input,
textarea {
    color: #0F172A !important;
    background-color: #FFFFFF !important;
    -webkit-text-fill-color: #0F172A !important;
    font-size: 0.95rem !important;
}

input::placeholder,
textarea::placeholder {
    color: #94A3B8 !important;
    -webkit-text-fill-color: #94A3B8 !important;
    opacity: 1 !important;
}

/* Number input step controls */
div[data-testid="stNumberInputStepDown"] button,
div[data-testid="stNumberInputStepUp"] button {
    background-color: #F8FAFC !important;
    color: #0F172A !important;
    border-color: #CBD5E1 !important;
}

div[data-testid="stNumberInputStepDown"] svg,
div[data-testid="stNumberInputStepUp"] svg {
    fill: #0F172A !important;
}

/* BaseWeb Select Box */
div[data-baseweb="select"] > div {
    background-color: #FFFFFF !important;
    color: #0F172A !important;
    border: 1.5px solid #CBD5E1 !important;
    border-radius: 12px !important;
}

div[data-baseweb="select"] span,
div[data-baseweb="select"] div {
    color: #0F172A !important;
}

div[data-baseweb="select"] svg {
    fill: #0F172A !important;
}

ul[role="listbox"] {
    background-color: #FFFFFF !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 12px !important;
    box-shadow: 0 10px 25px rgba(0,0,0,0.1) !important;
}

li[role="option"] {
    background-color: #FFFFFF !important;
    color: #0F172A !important;
}

li[role="option"]:hover,
li[role="option"][aria-selected="true"] {
    background-color: #ECFDF5 !important;
    color: #065F46 !important;
}

/* Tabs styling */
div[data-baseweb="tab-list"] {
    gap: 0.5rem;
    border-bottom: 2px solid #E2E8F0 !important;
    background: transparent !important;
}

button[data-baseweb="tab"] {
    background: transparent !important;
    border: none !important;
    color: #475569 !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    padding: 0.6rem 1.1rem !important;
    border-radius: 8px 8px 0 0 !important;
}

button[data-baseweb="tab"]:hover {
    color: #0F172A !important;
    background: rgba(16,185,129,0.06) !important;
}

button[data-baseweb="tab"][aria-selected="true"] {
    color: #10B981 !important;
    font-weight: 700 !important;
    border-bottom: 2px solid #10B981 !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #F8FAFC !important;
    border-right: 1px solid var(--line) !important;
}

section[data-testid="stSidebarContent"] {
    padding: 1rem 0.9rem !important;
}

/* Metric Containers */
div[data-testid="stMetricContainer"] {
    background: #FFFFFF !important;
    border: 1px solid var(--line) !important;
    border-radius: 18px !important;
    box-shadow: var(--shadow) !important;
    padding: 0.8rem 1rem !important;
}

div[data-testid="stMetricLabel"] p,
div[data-testid="stMetricLabel"] span {
    color: #475569 !important;
    font-weight: 600 !important;
    font-size: 0.86rem !important;
}

div[data-testid="stMetricValue"] {
    color: #0F172A !important;
    font-weight: 800 !important;
    letter-spacing: -0.04em !important;
}

/* Buttons */
.stButton > button {
    border: 1px solid var(--line) !important;
    border-radius: 12px !important;
    background: #FFFFFF !important;
    color: #0F172A !important;
    font-weight: 700 !important;
    padding: 0.55rem 1rem !important;
    transition: all 0.2s ease;
    box-shadow: none !important;
}

.stButton > button:hover {
    border-color: rgba(16,185,129,0.4) !important;
    color: #10B981 !important;
    transform: translateY(-1px);
}

button[kind="primary"], .stButton > button[kind="primary"] {
    background: linear-gradient(135deg, var(--green), var(--green-deep)) !important;
    color: #FFFFFF !important;
    border: none !important;
    box-shadow: 0 4px 14px rgba(16,185,129,0.25) !important;
}

button[kind="primary"]:hover {
    color: #FFFFFF !important;
    opacity: 0.95;
}

[data-testid="baseButton-primary"] {
    background: linear-gradient(135deg, var(--green), var(--green-deep)) !important;
    color: #FFFFFF !important;
    border: none !important;
}

/* Cards */
.card, .soft-card {
    background: #FFFFFF !important;
    border: 1px solid var(--line) !important;
    border-radius: 18px !important;
    box-shadow: var(--shadow) !important;
    padding: 1.1rem !important;
    color: #0F172A !important;
}

.card strong, .card b {
    color: #0F172A !important;
}

.card p, .card span {
    color: #334155;
}

.auth-shell {
    background: linear-gradient(180deg, #FFFFFF 0%, #F8FAFC 100%);
    border: 1px solid var(--line);
    border-radius: 24px;
    padding: 2.2rem;
    box-shadow: var(--shadow);
}

.hero-shell {
    background: linear-gradient(180deg, #FFFFFF 0%, #F8FAFC 100%);
    border: 1px solid var(--line);
    border-radius: 28px;
    padding: 2rem;
    box-shadow: var(--shadow);
}

.hero-title {
    font-size: clamp(2.6rem, 3.8vw, 4.4rem);
    line-height: 1.0;
    letter-spacing: -0.06em;
    margin: 0.6rem 0;
    font-weight: 900;
    color: #0F172A !important;
}

.hero-subtitle {
    margin-top: 0.8rem;
    color: #475569 !important;
    line-height: 1.65;
    font-size: 1.02rem;
}

.label-chip {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    background: #F1F5F9;
    color: #1E293B !important;
    border: 1px solid var(--line);
    border-radius: 999px;
    padding: 0.48rem 0.8rem;
    font-size: 0.78rem;
    font-weight: 700;
}

.feature-box {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    min-height: 160px;
    background: #FFFFFF;
    border: 1px solid var(--line);
    border-radius: 18px;
    box-shadow: var(--shadow);
    padding: 1.1rem;
}

.feature-icon {
    width: 52px;
    height: 52px;
    border-radius: 16px;
    background: var(--green-soft);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.4rem;
    margin-bottom: 0.7rem;
}

.sidebar-brand {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 1rem;
    padding-bottom: 0.8rem;
    border-bottom: 1px solid var(--line);
}

.brand-mark {
    width: 34px;
    height: 34px;
    border-radius: 10px;
    background: linear-gradient(135deg, #10B981, #059669);
    color: white !important;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.1rem;
    font-weight: 700;
}

.user-badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    background: #ECFDF5;
    color: #065F46 !important;
    border: 1px solid rgba(16,185,129,0.2);
    border-radius: 999px;
    padding: 0.38rem 0.7rem;
    font-size: 0.76rem;
    font-weight: 700;
    margin-bottom: 0.8rem;
}

/* Status Badges */
.pill-good, .pill-amber, .pill-red, .pill-blue {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    border-radius: 999px;
    padding: 0.3rem 0.65rem;
    font-size: 0.74rem;
    font-weight: 700;
}

.pill-good {
    background: var(--green-soft);
    color: #065F46 !important;
}

.pill-amber {
    background: var(--amber-soft);
    color: #92400E !important;
}

.pill-red {
    background: var(--red-soft);
    color: #991B1B !important;
}

.pill-blue {
    background: rgba(59,130,246,0.12);
    color: #1D4ED8 !important;
}

/* File Uploader Dropzone */
section[data-testid="stFileUploaderDropzone"] {
    background: #F8FAFC !important;
    border: 2px dashed rgba(16,185,129,0.5) !important;
    border-radius: 18px !important;
    padding: 1.4rem !important;
}

section[data-testid="stFileUploaderDropzone"] [data-testid="stMarkdownContainer"] p {
    color: #475569 !important;
}

section[data-testid="stFileUploaderDropzone"] button {
    background: #FFFFFF !important;
    color: #0F172A !important;
    border: 1.5px solid #CBD5E1 !important;
}

/* Dataframe Styling */
[data-testid="stDataFrameScrollWrapper"], .stDataFrame, .stDataFrame > div {
    background: #FFFFFF !important;
    border-radius: 12px !important;
}

/* Dark impact banner */
.dark-banner {
    background: linear-gradient(135deg, #0F172A 0%, #111827 60%, #0B1320 100%);
    border-radius: 24px;
    padding: 2.2rem;
    color: #FFFFFF !important;
    box-shadow: 0 14px 40px rgba(15,23,42,0.18);
}
.dark-banner h2, .dark-banner strong {
    color: #FFFFFF !important;
}
.dark-banner span, .dark-banner p {
    color: rgba(255,255,255,0.85) !important;
}

/* Demo Credentials Hint Box */
.demo-box {
    background: #F0FDF4;
    border: 1px solid rgba(16,185,129,0.25);
    border-radius: 12px;
    padding: 0.8rem 1rem;
    margin-top: 1rem;
}
.demo-box strong {
    color: #065F46 !important;
}
.demo-box span {
    color: #047857 !important;
    font-size: 0.84rem;
}

/* Production planning card */
.terminal-card {
    background: #FFFFFF;
    border: 1px solid var(--line);
    border-radius: 18px;
    padding: 1.2rem;
    box-shadow: var(--shadow);
    margin-bottom: 1rem;
}
</style>
"""

st.markdown(CSS, unsafe_allow_html=True)


def safe_inventory_dataframe(inventory_list: List[Dict[str, Any]]) -> pd.DataFrame:
    """Safe DataFrame constructor that guarantees all required columns are present with sensible defaults to prevent KeyError."""
    required_cols = [
        "item",
        "category",
        "quantity_kg",
        "expiry_hours",
        "status",
        "prepared_time",
        "location",
        "storage_condition",
        "contact",
    ]
    if not inventory_list:
        return pd.DataFrame(columns=required_cols)

    df = pd.DataFrame(inventory_list)
    defaults = {
        "item": "Prepared Food Item",
        "category": "Prepared Food",
        "quantity_kg": 10.0,
        "expiry_hours": 8,
        "status": "Good",
        "prepared_time": "Today, 11:30 AM",
        "location": "Main Kitchen Central Station",
        "storage_condition": "Chilled (4°C)",
        "contact": "Kitchen Duty Manager (+91 98765 43210)",
    }
    for col, default_val in defaults.items():
        if col not in df.columns:
            df[col] = default_val
        else:
            df[col] = df[col].fillna(default_val)
    return df


def seed_state():
    initial_data = load_initial_data()

    if "registered_users" not in st.session_state:
        st.session_state.registered_users = initial_data.get("registered_users", {})

    if "user" not in st.session_state:
        st.session_state.user = None

    if "page" not in st.session_state:
        st.session_state.page = "Home"

    if "inventory" not in st.session_state:
        st.session_state.inventory = [normalize_inventory_item(it) for it in initial_data.get("inventory", [])]
    else:
        # Guarantee every item currently in session state has full normalized keys
        st.session_state.inventory = [normalize_inventory_item(it) for it in st.session_state.inventory]

    if "ngos" not in st.session_state:
        st.session_state.ngos = initial_data.get("ngos", [])

    if "tasks" not in st.session_state:
        st.session_state.tasks = initial_data.get("tasks", [])

    if "kitchen_plan" not in st.session_state:
        st.session_state.kitchen_plan = initial_data.get(
            "kitchen_plan",
            {
                "day": "Monday",
                "meal_type": "Lunch",
                "plates": 400,
                "prepared_kg": 180.0,
                "predicted_surplus_plates": 44,
                "predicted_surplus_kg": 19.8,
                "waste_risk_kg": 19.8,
            },
        )

    if "analysis" not in st.session_state:
        st.session_state.analysis = {
            "freshness_percent": 92,
            "expiry_prediction": "18 hours",
            "status": "Good",
            "consumption_recommendation": "Redistribute within the next 12 hours while storage conditions remain safe.",
        }


def compute_inventory_status(expiry_hours: int) -> str:
    if expiry_hours <= 4:
        return "Expired"
    if expiry_hours <= 10:
        return "Near Expiry"
    return "Good"


def status_badge(value: Any) -> str:
    value_str = str(value)
    if value_str == "Good":
        return "<span class='pill-good'>Good</span>"
    if value_str == "Near Expiry":
        return "<span class='pill-amber'>Near Expiry</span>"
    if value_str == "Expired":
        return "<span class='pill-red'>Expired</span>"
    if value_str in ["Assigned", "Connected", "Claimed", "Delivered"]:
        return f"<span class='pill-good'>{value_str}</span>"
    if value_str in ["In Transit", "In Route"]:
        return "<span class='pill-amber'>In Transit</span>"
    if value_str == "Available":
        return "<span class='pill-blue'>Available</span>"
    return f"<span class='pill-good'>{value_str}</span>"


def logout_user():
    st.session_state.user = None
    st.session_state.page = "Home"
    st.rerun()


def render_sidebar():
    st.sidebar.markdown(
        """
        <div class='sidebar-brand'>
            <div class='brand-mark'>🌱</div>
            <div style='font-weight:800; font-size:1.1rem; color:#0F172A;'>FoodCycle AI</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.session_state.user:
        user = st.session_state.user
        st.sidebar.markdown(
            f"<div class='user-badge'>{user.get('role', 'Member')} · {user.get('name', 'User')}</div>",
            unsafe_allow_html=True,
        )

    pages = [
        "Home",
        "Dashboard",
        "Food Inventory",
        "Food Quality",
        "Redistribution Network",
        "Analytics & ESG",
    ]
    for page in pages:
        is_active = st.session_state.get("page") == page
        label = f"● {page}" if is_active else page
        btn_type = "primary" if is_active else "secondary"
        if st.sidebar.button(label, key=f"nav_{page}", type=btn_type, use_container_width=True):
            st.session_state.page = page
            st.rerun()

    if st.session_state.user:
        st.sidebar.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
        if st.sidebar.button("🚪 Logout", key="logout_button", use_container_width=True):
            logout_user()

    st.sidebar.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
    st.sidebar.caption("AI-powered food recovery platform · v2.1")


def render_auth_page():
    st.markdown(
        """
        <div style='text-align:center; margin-bottom:1.5rem;'>
            <div style='display:inline-flex; align-items:center; gap:0.5rem; margin-bottom:0.4rem;'>
                <span class='brand-mark'>🌱</span>
                <span style='font-size:1.8rem; font-weight:900; color:#0F172A;'>FoodCycle AI</span>
            </div>
            <p style='color:#475569; font-size:1.05rem; margin:0;'>Zero-waste food recovery, quality validation, and real-time redistribution</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    left, right = st.columns([1.2, 0.9])
    with left:
        st.markdown("<div class='auth-shell'>", unsafe_allow_html=True)
        tabs = st.tabs(["🔑 Log In", "📝 Register", "🚀 Continue as Guest"])

        with tabs[0]:
            with st.form("login_form"):
                email = st.text_input(
                    "Email address",
                    placeholder="Enter your email (e.g. demo@foodcycle.ai)",
                    help="Use your registered email or demo account.",
                )
                password = st.text_input(
                    "Password",
                    type="password",
                    placeholder="Enter your password",
                    help="Password for your account.",
                )
                col_sub1, col_sub2 = st.columns([1.2, 1])
                with col_sub1:
                    submitted = st.form_submit_button("Sign In to FoodCycle", type="primary", use_container_width=True)

                if submitted:
                    cleaned_email = email.strip().lower()
                    user_record = st.session_state.registered_users.get(cleaned_email)
                    if user_record and user_record.get("password") == password:
                        st.session_state.user = {
                            "name": user_record["name"],
                            "email": user_record["email"],
                            "role": user_record.get("role", "Member"),
                        }
                        st.session_state.page = "Home"
                        st.success(f"Welcome back, {user_record['name']}!")
                        st.rerun()
                    else:
                        st.error("Invalid email or password. Please check your credentials or use the demo login below.")

            # Quick Demo Login helper button outside the form for instant access
            st.markdown(
                """
                <div class='demo-box'>
                    <strong>💡 Demo Credentials:</strong><br>
                    <span>Email: <code>demo@foodcycle.ai</code> &nbsp;|&nbsp; Password: <code>demo123</code></span>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
            if st.button("⚡ 1-Click Demo Login", key="quick_demo_login_btn", use_container_width=True):
                st.session_state.user = {
                    "name": "Demo User",
                    "email": "demo@foodcycle.ai",
                    "role": "Kitchen Staff",
                }
                st.session_state.page = "Home"
                st.rerun()

        with tabs[1]:
            with st.form("register_form"):
                name = st.text_input("Full name", placeholder="Enter your full name (e.g. Alex Johnson)")
                reg_email = st.text_input("Email address", placeholder="Enter your email address", key="register_email")
                reg_password = st.text_input(
                    "Password",
                    type="password",
                    placeholder="Create a password (min. 6 characters)",
                    key="register_password",
                )
                role = st.selectbox("Role", ["Kitchen Staff", "NGO Partner", "Food Inspector", "Sustainability Manager"])
                reg_submitted = st.form_submit_button("Create Account", type="primary", use_container_width=True)

                if reg_submitted:
                    if not name.strip() or not reg_email.strip() or not reg_password:
                        st.warning("Please complete all required fields.")
                    elif len(reg_password) < 4:
                        st.warning("Password must be at least 4 characters long.")
                    else:
                        email_key = reg_email.strip().lower()
                        if email_key in st.session_state.registered_users:
                            st.error("An account with this email address already exists. Please log in.")
                        else:
                            new_user = {
                                "name": name.strip(),
                                "email": email_key,
                                "password": reg_password,
                                "role": role,
                            }
                            st.session_state.registered_users[email_key] = new_user
                            save_current_data(registered_users=st.session_state.registered_users)
                            st.session_state.user = {
                                "name": name.strip(),
                                "email": email_key,
                                "role": role,
                            }
                            st.session_state.page = "Home"
                            st.success("Account created successfully! Logging you in...")
                            st.rerun()

        with tabs[2]:
            st.markdown("<div class='card' style='margin-top:0.8rem;'>", unsafe_allow_html=True)
            st.write("Browse the platform with guest privileges without creating an account.")
            if st.button("Explore as Guest", key="guest_login_btn", type="primary", use_container_width=True):
                st.session_state.user = {"name": "Guest Visitor", "email": "guest@foodcycle.ai", "role": "Guest"}
                st.session_state.page = "Home"
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        summary = forecast_summary(st.session_state.inventory)
        esg = calculate_esg_metrics(st.session_state.inventory)
        st.markdown(
            f"""
            <div class='hero-shell'>
                <div style='font-size:0.82rem; color:#10B981; font-weight:800; text-transform:uppercase; letter-spacing:0.08em;'>Live Impact Snapshot</div>
                <h3 style='color:#0F172A; margin:0.8rem 0 0.5rem 0;'>Fewer losses. Maximum recovery.</h3>
                <p style='color:#475569; font-size:0.92rem; margin-bottom:1.2rem;'>Active recovery metrics tracked across partner kitchens and dispatch hubs.</p>
                <div style='display:grid; gap:0.9rem;'>
                    <div class='card' style='padding:0.9rem;'>
                        <strong style='display:block; font-size:1.8rem; color:#0F172A;'>{summary['donated']} kg</strong>
                        <span style='color:#475569; font-size:0.88rem;'>Surplus Food Recovered</span>
                    </div>
                    <div class='card' style='padding:0.9rem;'>
                        <strong style='display:block; font-size:1.8rem; color:#0F172A;'>{esg['carbon_saved']} kg</strong>
                        <span style='color:#475569; font-size:0.88rem;'>CO2 Emissions Avoided</span>
                    </div>
                    <div class='card' style='padding:0.9rem;'>
                        <strong style='display:block; font-size:1.8rem; color:#0F172A;'>{esg['food_recovery']}%</strong>
                        <span style='color:#475569; font-size:0.88rem;'>Food Recovery Efficiency</span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_home_page():
    st.markdown(
        """
        <div style='display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:0.8rem; margin-bottom:1.2rem;'>
            <div style='display:flex; align-items:center; gap:0.7rem;'>
                <span class='brand-mark'>🌱</span>
                <div style='font-weight:900; font-size:1.15rem; color:#0F172A;'>FoodCycle AI</div>
            </div>
            <div style='display:flex; gap:0.6rem; flex-wrap:wrap;'>
                <span class='label-chip'>AI Forecasting</span>
                <span class='label-chip'>Quality Inspection</span>
                <span class='label-chip'>Logistics Matching</span>
                <span class='label-chip'>ESG Analytics</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    left, right = st.columns([1.15, 0.95])
    with left:
        st.markdown("<div class='hero-shell'>", unsafe_allow_html=True)
        st.markdown(
            "<div style='color:#10B981; font-size:0.84rem; font-weight:800; letter-spacing:0.08em; text-transform:uppercase;'>Sustainable Food Recovery</div>",
            unsafe_allow_html=True,
        )
        st.markdown("<div class='hero-title'>Less Food Waste.<br>More Good Food.</div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='hero-subtitle'>Intelligent food redistribution platform connecting commercial kitchens, food safety inspectors, and community NGOs to eliminate surplus waste before spoilage occurs.</div>",
            unsafe_allow_html=True,
        )

        st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            if st.button("📊 Open Dashboard", key="home_dashboard_btn", type="primary", use_container_width=True):
                st.session_state.page = "Dashboard"
                st.rerun()
        with c2:
            if st.button("🔍 Run Quality Check", key="home_quality_btn", use_container_width=True):
                st.session_state.page = "Food Quality"
                st.rerun()

        st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
        chips = st.columns(4)
        for col, name in zip(chips, ["Predict Surplus", "Verify Freshness", "Dispatch Routes", "Measure ESG"]):
            with col:
                st.markdown(f"<div class='label-chip' style='width:100%;'>{name}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown(
            """
            <div class='hero-shell' style='padding:0.8rem; overflow:hidden;'>
                <img src='https://images.unsplash.com/photo-1546793665-c74683f339c1?auto=format&fit=crop&w=1200&q=80' alt='Fresh produce' style='width:100%; border-radius:18px; height:430px; object-fit:cover;' />
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='margin-top:2.4rem;'></div>", unsafe_allow_html=True)
    st.markdown(
        "<h2 style='color:#0F172A; margin-bottom:1.2rem; font-size:2.1rem; font-weight:900; letter-spacing:-0.05em;'>How It Works</h2>",
        unsafe_allow_html=True,
    )

    features = [
        ("🔮", "Surplus Prediction", "Forecasts kitchen surplus patterns and pinpoints high-risk stock prior to expiration."),
        ("📷", "AI Quality Inspector", "Analyzes food images and sensory descriptions for freshness assurance scoring."),
        ("🚚", "Smart Dispatch", "Instantly matches expiring food with nearby vetted NGOs, food banks, and shelters."),
        ("♻️", "ESG Impact Tracking", "Measures carbon offset, water conservation, and social meals distributed in real time."),
    ]
    cols = st.columns(4)
    for col, (icon, title, detail) in zip(cols, features):
        with col:
            st.markdown(
                f"<div class='feature-box'>"
                f"<div class='feature-icon'>{icon}</div>"
                f"<div style='font-weight:800; color:#0F172A; font-size:1.02rem; margin-bottom:0.35rem;'>{title}</div>"
                f"<div style='font-size:0.84rem; color:#475569; line-height:1.6;'>{detail}</div>"
                f"</div>",
                unsafe_allow_html=True,
            )

    st.markdown("<div style='margin-top:2.4rem;'></div>", unsafe_allow_html=True)
    st.markdown(
        """
        <div class='dark-banner'>
            <h2 style='font-size:2.2rem; margin:0 0 0.8rem 0; letter-spacing:-0.05em;'>Good food shouldn’t go to waste.</h2>
            <p style='margin:0; font-size:1.02rem;'>Transform surplus into immediate community impact with synchronized supply chain intelligence.</p>
            <div style='display:grid; grid-template-columns:repeat(4, minmax(0,1fr)); gap:1rem; margin-top:1.6rem;'>
                <div style='background:rgba(255,255,255,0.08); border:1px solid rgba(255,255,255,0.14); border-radius:14px; padding:1rem;'>
                    <strong style='display:block; font-size:2.2rem;'>30%</strong>
                    <span>Global food waste</span>
                </div>
                <div style='background:rgba(255,255,255,0.08); border:1px solid rgba(255,255,255,0.14); border-radius:14px; padding:1rem;'>
                    <strong style='display:block; font-size:2.2rem;'>1.3B</strong>
                    <span>Tons wasted yearly</span>
                </div>
                <div style='background:rgba(255,255,255,0.08); border:1px solid rgba(255,255,255,0.14); border-radius:14px; padding:1rem;'>
                    <strong style='display:block; font-size:2.2rem;'>-70%</strong>
                    <span>Target emissions cut</span>
                </div>
                <div style='background:rgba(255,255,255,0.08); border:1px solid rgba(255,255,255,0.14); border-radius:14px; padding:1rem;'>
                    <strong style='display:block; font-size:2.2rem;'>100%</strong>
                    <span>Actionable platform</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_dashboard_page():
    st.title("Operational Dashboard")
    summary = forecast_summary(st.session_state.inventory)

    metrics = st.columns(4)
    metric_data = [
        ("Total Food Prepared", f"{summary['prepared']} kg", "+5.1%"),
        ("Surplus Available", f"{summary['surplus']} kg", "+12.4%"),
        ("Food Donated", f"{summary['donated']} kg", "+18.2%"),
        ("Waste Avoided", f"{summary['waste_saved']} kg", "+7.9%"),
    ]
    for col, (label, value, delta) in zip(metrics, metric_data):
        col.metric(label, value, delta)

    trend = pd.DataFrame(
        {
            "Day": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
            "Prepared": [390, 420, 410, 460, 480, 470, 495],
            "Surplus": [90, 104, 120, 118, 140, 160, 148],
            "Donated": [60, 72, 78, 95, 110, 120, 128],
        }
    )

    st.markdown("<div style='margin-top:1.2rem;'></div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        fig = px.line(trend, x="Day", y=["Prepared", "Surplus"], markers=True, color_discrete_sequence=["#0F172A", "#F59E0B"])
        fig.update_layout(
            title="Food Prepared vs Surplus (kg)",
            template="plotly_white",
            legend_title_text="",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font={"color": "#0F172A", "family": "Inter"},
            xaxis={"title": "Day", "tickfont": {"color": "#475569"}, "gridcolor": "rgba(148,163,184,0.2)"},
            yaxis={"title": "Kilograms", "tickfont": {"color": "#475569"}, "gridcolor": "rgba(148,163,184,0.2)"},
            margin={"l": 20, "r": 10, "t": 40, "b": 20},
        )
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        bar_fig = px.bar(trend, x="Day", y="Donated", color_discrete_sequence=["#10B981"])
        bar_fig.update_layout(
            title="Food Donated to Partner Network (kg)",
            template="plotly_white",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font={"color": "#0F172A", "family": "Inter"},
            xaxis={"title": "Day", "tickfont": {"color": "#475569"}, "gridcolor": "rgba(148,163,184,0.2)"},
            yaxis={"title": "Kilograms", "tickfont": {"color": "#475569"}, "gridcolor": "rgba(148,163,184,0.2)"},
            margin={"l": 20, "r": 10, "t": 40, "b": 20},
        )
        st.plotly_chart(bar_fig, use_container_width=True)

    st.markdown("<div style='margin-top:1.6rem;'></div>", unsafe_allow_html=True)
    st.subheader("Current Live Inventory Snapshot")
    if st.session_state.inventory:
        inv_df = safe_inventory_dataframe(st.session_state.inventory)
        inv_display = inv_df[["item", "category", "quantity_kg", "expiry_hours", "status"]]
        inv_display.columns = ["Item Name", "Category", "Quantity (kg)", "Expiry Hours", "Status"]
        st.dataframe(inv_display, use_container_width=True, hide_index=True)
    else:
        st.info("No items currently in inventory. Add food items in the Food Inventory tab.")


def render_inventory_page():
    st.title("Food Inventory & Kitchen Operations")
    st.markdown("<p style='color:#475569; margin-top:-0.5rem;'>Kitchen production planning, surplus broadcasting, and live inventory control.</p>", unsafe_allow_html=True)

    kitchen_tabs = st.tabs([
        "🍳 Kitchen Production Terminal",
        "📢 Post Surplus for NGOs",
        "➕ Standard Item Entry",
    ])

    # ---------------- TAB 1: KITCHEN PRODUCTION PLANNING ----------------
    with kitchen_tabs[0]:
        st.markdown("<div class='terminal-card'>", unsafe_allow_html=True)
        st.markdown("<h4 style='margin-top:0;'>Daily Meal Volume & Waste Prediction Terminal</h4>", unsafe_allow_html=True)
        st.write("Input planned kitchen volume to estimate expected consumption, surplus variance, and prevent waste before it happens.")

        kp1, kp2, kp3 = st.columns([1.2, 1.2, 1.2])
        with kp1:
            plan_day = st.selectbox(
                "Select Day of Week",
                ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
                index=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"].index(
                    st.session_state.kitchen_plan.get("day", "Monday")
                ),
                key="kp_day_select",
            )
        with kp2:
            plan_meal = st.selectbox(
                "Meal Type / Category",
                ["Lunch", "Dinner", "Event catering", "Breakfast"],
                index=["Lunch", "Dinner", "Event catering", "Breakfast"].index(
                    st.session_state.kitchen_plan.get("meal_type", "Lunch")
                ),
                key="kp_meal_select",
            )
        with kp3:
            plan_plates = st.number_input(
                "Plates / Meals Prepared",
                min_value=10,
                max_value=10000,
                value=int(st.session_state.kitchen_plan.get("plates", 400)),
                step=25,
                key="kp_plates_input",
                help="Estimated number of meal portions prepared for this service.",
            )

        # Real-time waste prediction calculation
        prediction = predict_kitchen_waste(plan_day, plan_meal, int(plan_plates))

        st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Food Volume", f"{prediction['total_prepared_kg']} kg", f"{plan_plates} plates")
        m2.metric("Predicted Surplus", f"{prediction['predicted_surplus_plates']} plates", f"{prediction['predicted_surplus_kg']} kg")
        m3.metric("Landfill Waste Risk", f"{prediction['predicted_surplus_kg']} kg", f"{prediction['surplus_rate_pct']}% rate")
        m4.metric("CO2 Avoidable", f"{prediction['co2_avoidable_kg']} kg CO2", f"{prediction['water_avoidable_liters']} L water")

        st.markdown(
            f"""
            <div style='background:#F0FDF4; border:1px solid rgba(16,185,129,0.3); border-radius:12px; padding:0.85rem 1.1rem; margin:1rem 0;'>
                <strong style='color:#065F46;'>💡 Production Forecast Insight:</strong>
                <span style='color:#047857;'>
                    For <b>{plan_day} {plan_meal}</b>, model projects <b>~{prediction['safe_consumption_plates']} plates</b> consumed on-site.
                    Pre-scheduling pickup for the anticipated <b>{prediction['predicted_surplus_plates']} surplus plates ({prediction['predicted_surplus_kg']} kg)</b> will eliminate waste.
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        col_save, _ = st.columns([1.5, 2])
        with col_save:
            if st.button("💾 Save Production Plan & Sync Forecast", type="primary", use_container_width=True, key="save_kp_btn"):
                st.session_state.kitchen_plan = {
                    "day": plan_day,
                    "meal_type": plan_meal,
                    "plates": int(plan_plates),
                    "prepared_kg": prediction["total_prepared_kg"],
                    "predicted_surplus_plates": prediction["predicted_surplus_plates"],
                    "predicted_surplus_kg": prediction["predicted_surplus_kg"],
                    "waste_risk_kg": prediction["predicted_surplus_kg"],
                }
                save_current_data(kitchen_plan=st.session_state.kitchen_plan)
                st.success(f"Saved {plan_day} {plan_meal} production forecast into operational plan!")
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

    # ---------------- TAB 2: NGO SURPLUS FOOD LOGGING ----------------
    with kitchen_tabs[1]:
        st.markdown("<div class='terminal-card'>", unsafe_allow_html=True)
        st.markdown("<h4 style='margin-top:0;'>Post Excess Surplus Directly for NGO Pickup</h4>", unsafe_allow_html=True)
        st.write("Post surplus batches directly to the live Redistribution Network so community shelters and food banks can claim and route pickups in real time.")

        with st.form("ngo_surplus_upload_form"):
            col_s1, col_s2 = st.columns([1.8, 1.2])
            with col_s1:
                surplus_name = st.text_input(
                    "Food Name / Detailed Description",
                    placeholder="e.g. Cooked Basmati Rice & Dal Makhani",
                    help="Describe the food clearly for NGO meal planning.",
                )
            with col_s2:
                surplus_cat = st.selectbox("Category", FOOD_CATEGORIES, index=0)

            col_s3, col_s4, col_s5 = st.columns(3)
            with col_s3:
                surplus_kg = st.number_input("Quantity Available (kg)", min_value=1.0, value=25.0, step=1.0)
            with col_s4:
                surplus_window = st.selectbox(
                    "Expiry / Freshness Window",
                    ["Good for 2 hours", "Good for 4 hours", "Good for 6 hours", "Good for 12 hours", "Good for 24 hours"],
                    index=2,
                )
            with col_s5:
                surplus_condition = st.selectbox(
                    "Storage / Transport Condition",
                    ["Hot insulated (>65°C)", "Chilled cold chain (4°C)", "Packaged / Ready to Eat", "Ambient / Dry"],
                    index=0,
                )

            col_s6, col_s7 = st.columns(2)
            with col_s6:
                surplus_loc = st.text_input(
                    "Pickup Location / Loading Bay",
                    value="Central Kitchen Hub, Bay 2",
                    placeholder="e.g. Loading Dock Gate 3",
                )
            with col_s7:
                surplus_contact = st.text_input(
                    "Contact Person & Phone Number",
                    value="Chef Marcus (+91 98765 43210)",
                    placeholder="e.g. Kitchen Duty Manager (+91 ...)",
                )

            submitted_surplus = st.form_submit_button(
                "🚀 Broadcast Surplus to NGO Network", type="primary", use_container_width=True
            )
            if submitted_surplus:
                if surplus_name.strip():
                    # Parse hours from window
                    hours_val = 6
                    try:
                        hours_val = int(surplus_window.split()[2])
                    except Exception:
                        hours_val = 6

                    new_surplus_item = {
                        "id": f"surplus_{int(time.time() * 1000)}",
                        "item": surplus_name.strip(),
                        "category": surplus_cat,
                        "quantity_kg": float(surplus_kg),
                        "expiry_hours": hours_val,
                        "status": compute_inventory_status(hours_val),
                        "prepared_time": "Today, Just Cooked",
                        "location": surplus_loc.strip() or "Central Kitchen Bay 1",
                        "storage_condition": surplus_condition,
                        "contact": surplus_contact.strip() or "Kitchen Duty Staff",
                    }
                    st.session_state.inventory.append(new_surplus_item)
                    save_current_data(inventory=st.session_state.inventory)
                    st.success(f"Surplus batch '{surplus_name.strip()}' ({surplus_kg} kg) broadcasted! Visible to all NGOs on Redistribution Network.")
                    st.rerun()
                else:
                    st.warning("Please provide a name or description for the surplus food item.")

        st.markdown("</div>", unsafe_allow_html=True)

    # ---------------- TAB 3: STANDARD INVENTORY BATCH ENTRY ----------------
    with kitchen_tabs[2]:
        with st.form("inventory_form"):
            st.markdown("<h4 style='margin-top:0;'>Add Standard Inventory Batch</h4>", unsafe_allow_html=True)
            c1, c2, c3, c4 = st.columns([1.5, 1, 1, 1.2])
            with c1:
                item_name = st.text_input("Item Name", placeholder="e.g. Cooked Basmati Rice, Fresh Greens")
            with c2:
                quantity = st.number_input("Quantity (kg)", min_value=0.5, value=12.0, step=1.0)
            with c3:
                expiry = st.number_input("Expiry (hours)", min_value=1, max_value=168, value=10)
            with c4:
                category = st.selectbox("Category", FOOD_CATEGORIES, key="std_cat_select")

            submitted = st.form_submit_button("➕ Add Item to Inventory", type="primary", use_container_width=True)
            if submitted:
                if item_name.strip():
                    new_item = {
                        "id": f"item_{int(time.time() * 1000)}",
                        "item": item_name.strip(),
                        "quantity_kg": float(quantity),
                        "expiry_hours": int(expiry),
                        "status": compute_inventory_status(int(expiry)),
                        "category": category,
                        "prepared_time": "Today, Recent Batch",
                        "location": "Main Kitchen Hub",
                        "storage_condition": "Standard Stored",
                        "contact": "Kitchen Duty (+91 98765 43210)",
                    }
                    st.session_state.inventory.append(new_item)
                    save_current_data(inventory=st.session_state.inventory)
                    st.success(f"Added {item_name.strip()} ({quantity} kg) to inventory.")
                    st.rerun()
                else:
                    st.warning("Please provide a name for the food item.")

    st.markdown("<div style='margin-top:2rem;'></div>", unsafe_allow_html=True)
    head_c1, head_c2 = st.columns([3, 1])
    with head_c1:
        st.subheader("Live Inventory Tracker")
    with head_c2:
        if st.button("↺ Reset to Sample Inventory", key="reset_inv_btn", use_container_width=True):
            defaults = load_initial_data()
            st.session_state.inventory = [normalize_inventory_item(it) for it in defaults.get("inventory", [])]
            save_current_data(inventory=st.session_state.inventory)
            st.success("Reset inventory to initial demo items.")
            st.rerun()

    if st.session_state.inventory:
        inv_df = safe_inventory_dataframe(st.session_state.inventory)
        display_cols = ["item", "category", "quantity_kg", "expiry_hours", "status", "prepared_time", "location"]
        inv_display = inv_df[display_cols].copy()
        inv_display.columns = ["Item Name", "Category", "Quantity (kg)", "Expiry (hrs)", "Status", "Prepared Time", "Pickup Location"]
        st.dataframe(inv_display, use_container_width=True, hide_index=True)
    else:
        st.info("The inventory is currently empty. Use the tabs above to log kitchen production or surplus food.")

    st.markdown("<div style='margin-top:1.8rem;'></div>", unsafe_allow_html=True)
    st.markdown("<h4>Inventory Item Cards</h4>", unsafe_allow_html=True)

    if not st.session_state.inventory:
        st.write("No items to display.")
    else:
        cards = st.columns(3)
        for idx, item in enumerate(st.session_state.inventory):
            with cards[idx % 3]:
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                st.markdown(f"<strong style='font-size:1.1rem; color:#0F172A;'>{item.get('item', 'Food Item')}</strong>", unsafe_allow_html=True)
                st.markdown(f"<div style='color:#475569; margin:0.3rem 0;'>Category: <b>{item.get('category', 'Prepared Food')}</b></div>", unsafe_allow_html=True)
                st.markdown(f"<div style='color:#475569;'>Quantity: <b>{item.get('quantity_kg', 0.0)} kg</b></div>", unsafe_allow_html=True)
                st.markdown(f"<div style='color:#475569;'>Expiry: <b>{item.get('expiry_hours', 0)} hours</b></div>", unsafe_allow_html=True)
                st.markdown(f"<div style='color:#475569; font-size:0.82rem;'>Location: {item.get('location', 'Main Hub')}</div>", unsafe_allow_html=True)
                st.markdown(f"<div style='margin:0.5rem 0;'>{status_badge(item.get('status', 'Good'))}</div>", unsafe_allow_html=True)

                st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
                item_id = item.get("id", f"idx_{idx}")
                if st.button("🗑️ Delete Item", key=f"del_item_{item_id}", use_container_width=True):
                    st.session_state.inventory = [it for it in st.session_state.inventory if it.get("id", f"idx_{idx}") != item_id]
                    save_current_data(inventory=st.session_state.inventory)
                    st.success(f"Removed {item.get('item', 'Item')}.")
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)
                st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)


def render_quality_page():
    st.title("AI Food Quality Inspector")
    st.markdown("<p style='color:#475569; margin-top:-0.5rem;'>Validate freshness, detect early spoilage, and receive real-time shelf life predictions.</p>", unsafe_allow_html=True)

    c1, c2 = st.columns([1.1, 1.2])
    with c1:
        uploaded = st.file_uploader(
            "Upload food batch photo (optional)",
            type=["png", "jpg", "jpeg", "webp"],
            help="High-contrast clear photos produce the most accurate freshness assessments.",
        )
        if uploaded is not None:
            image = Image.open(uploaded)
            st.image(image, caption="Uploaded Food Sample", use_container_width=True)

    with c2:
        description = st.text_area(
            "Describe the item, storage condition, and aroma/appearance",
            value="Fresh cooked dal stored in a chilled condition, no visible mold, prepared from the kitchen line.",
            placeholder="e.g. Steamed rice stored at 4°C, safe container, prepared 3 hours ago.",
            height=135,
        )

        if st.button("🔬 Analyze Food Quality", type="primary", use_container_width=True):
            with st.spinner("Analyzing food sample with AI inspection engine..."):
                result = analyze_food_quality(uploaded, description)
                st.session_state.analysis = result
                st.session_state.analysis_desc = description
                st.success("Food inspection analysis completed.")

    result = st.session_state.analysis
    st.markdown("<div style='margin-top:1.6rem;'></div>", unsafe_allow_html=True)
    st.subheader("Inspection Assessment")

    q1, q2, q3 = st.columns(3)
    q1.metric("Freshness Rating", f"{result['freshness_percent']}%")
    q2.metric("Predicted Shelf Life", result["expiry_prediction"])
    q3.metric("Safety Status", result["status"])

    st.markdown("<div style='margin-top:1rem;'></div>", unsafe_allow_html=True)
    status_val = result.get("status", "Good")
    if status_val == "Good":
        st.success(f"✅ **Recommendation:** {result['consumption_recommendation']}")
    elif status_val == "Near Expiry":
        st.warning(f"⚠️ **Recommendation:** {result['consumption_recommendation']}")
    else:
        st.error(f"🛑 **Recommendation:** {result['consumption_recommendation']}")

    # Connected Action: Transfer inspected item directly into inventory
    st.markdown("<div style='margin-top:1.2rem;'></div>", unsafe_allow_html=True)
    with st.expander("📦 Add Inspected Item Directly into Inventory", expanded=False):
        with st.form("add_inspected_form"):
            default_name = description.split(",")[0].strip() if description else "Inspected Food Item"
            inspected_name = st.text_input("Item Name", value=default_name[:40])
            inspected_qty = st.number_input("Batch Quantity (kg)", min_value=1.0, value=15.0, step=1.0)
            inspected_cat = st.selectbox("Category", FOOD_CATEGORIES, index=3)
            add_sub = st.form_submit_button("Add to Live Inventory", type="primary", use_container_width=True)

            if add_sub:
                new_entry = {
                    "id": f"item_{int(time.time() * 1000)}",
                    "item": inspected_name.strip(),
                    "quantity_kg": float(inspected_qty),
                    "expiry_hours": 18 if result["status"] == "Good" else (6 if result["status"] == "Near Expiry" else 2),
                    "status": result["status"],
                    "category": inspected_cat,
                    "prepared_time": "Today, Quality Verified",
                    "location": "Quality Inspection Station",
                    "storage_condition": "Inspected & Approved",
                    "contact": "Quality Inspector",
                }
                st.session_state.inventory.append(new_entry)
                save_current_data(inventory=st.session_state.inventory)
                st.success(f"Successfully added {inspected_name.strip()} ({inspected_qty} kg) to live inventory!")
                st.rerun()

    if not os.getenv("GEMINI_API_KEY"):
        st.caption("ℹ️ Gemini API key is optional. App is using high-precision heuristic inspection modeling.")


def render_redist_page():
    st.title("Redistribution Network & Logistics")
    st.markdown("<p style='color:#475569; margin-top:-0.5rem;'>Connect kitchen surplus directly with nearby community hubs, shelters, and food banks.</p>", unsafe_allow_html=True)

    # ---------------- DEDICATED NGO SECTION: AVAILABLE SURPLUS TO CLAIM ----------------
    st.markdown("<h3>📦 Available Surplus Batches for Immediate NGO Claim</h3>", unsafe_allow_html=True)
    available_surplus = [it for it in st.session_state.inventory if it.get("status") in ["Good", "Near Expiry"]]

    if not available_surplus:
        st.info("No surplus food batches are currently pending claim. Kitchen staff can post batches in the Food Inventory tab.")
    else:
        surplus_cols = st.columns(3)
        for idx, s_item in enumerate(available_surplus):
            with surplus_cols[idx % 3]:
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                st.markdown(f"<strong style='font-size:1.15rem; color:#0F172A;'>{s_item.get('item', 'Food Batch')}</strong>", unsafe_allow_html=True)
                st.markdown(f"<div style='color:#10B981; font-weight:700; font-size:0.92rem; margin:0.2rem 0;'>{s_item.get('quantity_kg', 0.0)} kg &nbsp;·&nbsp; ~{int(s_item.get('quantity_kg', 0.0) * 2.2)} Portions</div>", unsafe_allow_html=True)
                st.markdown(f"<div style='color:#475569; font-size:0.86rem;'><b>Category:</b> {s_item.get('category', 'Prepared Food')}</div>", unsafe_allow_html=True)
                st.markdown(f"<div style='color:#475569; font-size:0.86rem;'><b>Freshness:</b> {s_item.get('expiry_hours', 6)} hrs remaining</div>", unsafe_allow_html=True)
                st.markdown(f"<div style='color:#475569; font-size:0.86rem;'><b>Condition:</b> {s_item.get('storage_condition', 'Chilled')}</div>", unsafe_allow_html=True)
                st.markdown(f"<div style='color:#475569; font-size:0.86rem;'><b>Location:</b> {s_item.get('location', 'Central Kitchen Hub')}</div>", unsafe_allow_html=True)
                st.markdown(f"<div style='color:#475569; font-size:0.86rem; margin-bottom:0.5rem;'><b>Contact:</b> {s_item.get('contact', 'Kitchen Staff')}</div>", unsafe_allow_html=True)
                st.markdown(status_badge(s_item.get("status", "Good")), unsafe_allow_html=True)

                st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
                # NGO selection for claim
                ngo_names = [n["name"] for n in st.session_state.ngos]
                claimant_ngo_name = st.selectbox(
                    "Claiming NGO Partner",
                    ngo_names,
                    key=f"select_ngo_for_{s_item['id']}",
                )
                claimant_ngo = next((n for n in st.session_state.ngos if n["name"] == claimant_ngo_name), st.session_state.ngos[0])

                if st.button("⚡ Claim Surplus Batch", key=f"claim_batch_{s_item['id']}", type="primary", use_container_width=True):
                    success, message = claim_specific_food_item(claimant_ngo, s_item["id"], st.session_state.inventory, st.session_state.tasks)
                    if success:
                        st.success(message)
                    else:
                        st.warning(message)
                    st.rerun()

                st.markdown("</div>", unsafe_allow_html=True)
                st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)

    st.markdown("<div style='margin-top:2rem;'></div>", unsafe_allow_html=True)
    st.subheader("Partner Organizations Overview")
    ngo_table = pd.DataFrame(st.session_state.ngos)[["name", "type", "distance_km", "capacity_kg", "status"]]
    ngo_table.columns = ["Partner Organization", "Type", "Distance (km)", "Capacity (kg)", "Current Status"]
    st.dataframe(ngo_table, use_container_width=True, hide_index=True)

    st.markdown("<div style='margin-top:1.5rem;'></div>", unsafe_allow_html=True)
    st.subheader("Partner Network Operations")

    ngo_cols = st.columns(4)
    for idx, ngo in enumerate(st.session_state.ngos):
        with ngo_cols[idx % 4]:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown(f"<strong style='font-size:1.05rem; color:#0F172A;'>{ngo['name']}</strong>", unsafe_allow_html=True)
            st.markdown(f"<div style='color:#475569; margin:0.3rem 0;'>Distance: <b>{ngo['distance_km']} km</b></div>", unsafe_allow_html=True)
            st.markdown(f"<div style='color:#475569;'>Capacity: <b>{ngo['capacity_kg']} kg</b></div>", unsafe_allow_html=True)
            st.markdown(f"<div style='color:#475569; margin-bottom:0.6rem;'>Type: <b>{ngo['type']}</b></div>", unsafe_allow_html=True)
            st.markdown(status_badge(ngo["status"]), unsafe_allow_html=True)

            st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)

            if ngo.get("status") in ["Connected", "Claimed"]:
                if st.button("✅ Complete Delivery", key=f"complete_{ngo['name']}", type="primary", use_container_width=True):
                    success, message = complete_or_reset_partner(ngo, st.session_state.tasks)
                    if success:
                        st.success(message)
                    st.rerun()
            else:
                if st.button("🚚 Auto Match & Route", key=f"connect_{ngo['name']}", use_container_width=True):
                    success, message = connect_partner(ngo, st.session_state.inventory, st.session_state.tasks)
                    if success:
                        st.success(message)
                    else:
                        st.warning(message)
                    st.rerun()

                if st.button("📦 Auto Claim Surplus", key=f"claim_{ngo['name']}", use_container_width=True):
                    success, message = claim_food_for_partner(ngo, st.session_state.inventory, st.session_state.tasks)
                    if success:
                        st.success(message)
                    else:
                        st.warning(message)
                    st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)

    st.markdown("<div style='margin-top:1.8rem;'></div>", unsafe_allow_html=True)
    st.subheader("Live Route Tracking & Dispatches")
    if st.session_state.tasks:
        tasks_df = pd.DataFrame(st.session_state.tasks)
        col_subset = [c for c in ["task", "recipient", "status", "eta", "location", "contact"] if c in tasks_df.columns]
        display_task_df = tasks_df[col_subset].copy()
        col_rename = {
            "task": "Task Description",
            "recipient": "Recipient / Hub",
            "status": "Status",
            "eta": "ETA",
            "location": "Pickup Bay",
            "contact": "Contact Person",
        }
        display_task_df.rename(columns=col_rename, inplace=True)
        st.dataframe(display_task_df, use_container_width=True, hide_index=True)
    else:
        st.info("No active dispatch routes.")

    st.markdown("<div style='margin-top:1.4rem;'></div>", unsafe_allow_html=True)
    st.subheader("Redistribution Network Map")
    route_df = pd.DataFrame(
        {
            "lat": [12.9816, 12.9734, 12.9685, 12.9922],
            "lon": [77.5940, 77.6030, 77.6102, 77.5814],
            "name": ["Central Kitchen Hub", "Local NGOs Hub", "Hope Shelter Network", "Community Care Kitchen"],
        }
    )
    st.map(route_df)


def render_analytics_page():
    st.title("Analytics & ESG Sustainability Impact")
    metrics = calculate_esg_metrics(st.session_state.inventory)
    summary = forecast_summary(st.session_state.inventory)

    cards = st.columns(4)
    card_data = [
        ("Carbon Offset", f"{metrics['carbon_saved']} kg CO2", "-14% vs baseline"),
        ("Water Saved", f"{metrics['water_saved']} Liters", "+22% conserved"),
        ("Food Recovery Rate", f"{metrics['food_recovery']}%", "Industry High"),
        ("Composite ESG Score", f"{metrics['esg_score']} / 100", "Grade A"),
    ]
    for col, (label, value, delta) in zip(cards, card_data):
        col.metric(label, value, delta)

    st.markdown("<div style='margin-top:1.6rem;'></div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        waste_df = pd.DataFrame(
            {
                "Day": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
                "Waste Avoided": [120, 110, 97, 88, 84, 71, 66],
                "Food Recovered": [70, 88, 96, 109, 118, 126, 132],
            }
        )
        fig = px.line(
            waste_df,
            x="Day",
            y=["Waste Avoided", "Food Recovered"],
            markers=True,
            color_discrete_sequence=["#EF4444", "#10B981"],
        )
        fig.update_layout(
            title="Surplus Avoided vs Recovered (kg)",
            template="plotly_white",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font={"color": "#0F172A", "family": "Inter"},
            xaxis={"title": "Day", "tickfont": {"color": "#475569"}, "gridcolor": "rgba(148,163,184,0.2)"},
            yaxis={"title": "Kilograms", "tickfont": {"color": "#475569"}, "gridcolor": "rgba(148,163,184,0.2)"},
            margin={"l": 20, "r": 10, "t": 40, "b": 20},
        )
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        pie = px.pie(
            values=[metrics["carbon_saved"], max(1.0, 150.0 - metrics["carbon_saved"])],
            names=["Carbon Saved (CO2)", "Operational Footprint"],
            color_discrete_sequence=["#10B981", "#E2E8F0"],
            hole=0.45,
        )
        pie.update_layout(
            title="Carbon Footprint Mitigation Share",
            template="plotly_white",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font={"color": "#0F172A", "family": "Inter"},
            margin={"l": 20, "r": 10, "t": 40, "b": 20},
        )
        st.plotly_chart(pie, use_container_width=True)

    st.markdown("<div style='margin-top:1.6rem;'></div>", unsafe_allow_html=True)
    st.subheader("Audited ESG Compliance Report")

    total_kg = round(sum(float(item.get("quantity_kg", 0)) for item in st.session_state.inventory), 1)
    surplus_kg = round(
        sum(float(item.get("quantity_kg", 0)) for item in st.session_state.inventory if item.get("status") in ["Near Expiry", "Expired"]) * 0.7,
        1,
    )

    report = pd.DataFrame(
        [
            {
                "Total Inventory Handled (kg)": total_kg,
                "Surplus Identified (kg)": surplus_kg,
                "Food Donated to NGOs (kg)": summary["donated"],
                "Landfill Waste Avoided (kg)": summary["waste_saved"],
                "Carbon Emissions Saved (kg CO2)": metrics["carbon_saved"],
                "Water Conserved (Liters)": metrics["water_saved"],
                "Social Meals Equivalent": int(summary["donated"] * 2.2),
                "ESG Rating Score": f"{metrics['esg_score']}/100",
            }
        ]
    )
    st.dataframe(report, use_container_width=True, hide_index=True)

    st.markdown("<div style='margin-top:1rem;'></div>", unsafe_allow_html=True)
    csv = report.to_csv(index=False).encode("utf-8")
    st.download_button(
        "📥 Download Official ESG Compliance Report (CSV)",
        csv,
        file_name="foodcycle_esg_compliance_report.csv",
        mime="text/csv",
        type="primary",
        use_container_width=True,
    )


def main():
    seed_state()

    if not st.session_state.user:
        render_auth_page()
        return

    render_sidebar()

    pages = {
        "Home": render_home_page,
        "Dashboard": render_dashboard_page,
        "Food Inventory": render_inventory_page,
        "Food Quality": render_quality_page,
        "Redistribution Network": render_redist_page,
        "Analytics & ESG": render_analytics_page,
    }
    pages.get(st.session_state.page, render_home_page)()


if __name__ == "__main__":
    main()
