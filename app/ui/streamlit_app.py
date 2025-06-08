# app/api/main.py
from fastapi import FastAPI
from pymongo import MongoClient
from bson import ObjectId
import os
import streamlit as st
import requests

app = FastAPI()

ENV = os.getenv("ENV", "DEV").upper()

if ENV == "DEV":
    API_URL = "http://localhost:8000"
elif ENV in ["TEST", "PROD"]:
    API_URL = os.getenv("API_URL")
else:
    raise ValueError("Invalid ENV variable. Must be DEV, TEST, or PROD.")

st.title("📊 Supabase Snapshot Explorer")

section = st.sidebar.radio("Select an endpoint", [
    "Fraudulent Charges",
    "Active Subscriptions",
    "3D Secure Payments",
    "Customer by ID",
    "Summary View"
])

def safe_json(endpoint):
    resp = requests.get(f"{API_URL}{endpoint}")
    if resp.status_code == 200:
        try:
            return resp.json()
        except Exception:
            st.error("Error parsing JSON response.")
            st.text(resp.text)
            return None
    else:
        st.error(f"HTTP Error {resp.status_code}")
        st.text(resp.text)
        return None

if section == "Fraudulent Charges":
    st.header("💥 Potentially Fraudulent Charges")
    data = safe_json("/charges/fraud")
    if data:
        for item in data:
            st.write(f"💳 Method: {item['_id']}")
            st.write(f"💰 Total: €{item['total'] / 100:.2f} ({item['count']} times)")
            st.divider()

elif section == "Active Subscriptions":
    st.header("📦 Active Subscriptions")
    data = safe_json("/subscriptions/active")
    if data:
        for sub in data:
            st.subheader(f"🔗 {sub['id']}")
            st.write(f"👤 Customer: {sub['customer_id']}")
            st.write(f"💶 Price ID: {sub['price_id']} — Status: {sub['status']}")
            st.write(f"📅 Start Date: {sub['start_date']}")
            if 'items' in sub and 'data' in sub['items'] and len(sub['items']['data']) > 0:
                plan = sub['items']['data'][0].get('plan', {})
                st.write(f"🪙 Amount: €{plan.get('amount', 0) / 100:.2f} — {plan.get('interval', 'unknown')}")
            st.divider()

elif section == "3D Secure Payments":
    st.header("🔐 Payments with 3D Secure")
    data = safe_json("/payment_intents/3ds")
    if data:
        for p in data:
            st.write(f"🆔 {p['id']} — 💶 €{p['amount'] / 100:.2f}")
            st.write(f"👤 Customer: {p['customer_id']} — Method: {p['payment_method']}")
            st.write(f"📅 Created: {p['created']} — Status: {p['status']}")
            st.divider()

elif section == "Customer by ID":
    st.header("👤 Customer Information")
    customer_list = safe_json("/customers")

    if customer_list:
        options = {
            f"{c.get('name', 'Unknown')} ({c.get('email', 'no-email')})": c.get('id', '')
            for c in customer_list if 'id' in c
        }

        selected_label = st.selectbox("Select a customer", list(options.keys()))
        customer_id = options[selected_label]

        data = safe_json(f"/customers/{customer_id}")
        if data:
            st.write(f"📧 {data.get('email')} — 👤 {data.get('name')}")
            st.write(f"💳 Payment Method ID: {data.get('default_payment_method_id')}")
            st.write(f"📅 Created: {data.get('created')}")
            st.write(f"💶 Balance: €{data.get('balance', 0) / 100:.2f}")

elif section == "Summary View":
    st.header("📈 Summary View")
    data = safe_json("/subscriptions/active")
    if data:
        st.subheader("📊 Total Active Subscriptions")
        st.metric(label="Count", value=len(data))

        total_amount = 0
        for sub in data:
            if 'items' in sub and 'data' in sub['items'] and len(sub['items']['data']) > 0:
                plan = sub['items']['data'][0].get('plan', {})
                total_amount += plan.get('amount', 0)
        st.metric(label="Estimated Monthly Revenue (EUR)", value=f"€{total_amount / 100:.2f}")
