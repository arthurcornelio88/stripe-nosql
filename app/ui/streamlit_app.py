# app/api/main.py
from fastapi import FastAPI
from pymongo import MongoClient
from bson import ObjectId
import os
import streamlit as st
import requests
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

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
    "Subscription Status",
    "3D Secure Payments", 
    "Customer by ID",
    "Summary View",
    "Analytics Dashboard"
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

elif section == "Subscription Status":
    st.header("📦 Subscription Status Overview")
    
    # Get all subscriptions (not just active)
    all_subs = safe_json("/subscriptions")
    if all_subs:
        # Create status filter
        statuses = list(set([sub.get('status', 'unknown') for sub in all_subs]))
        selected_statuses = st.multiselect(
            "Filter by status:", 
            statuses, 
            default=statuses
        )
        
        # Filter subscriptions
        filtered_subs = [sub for sub in all_subs if sub.get('status') in selected_statuses]
        
        # Status summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        status_counts = {}
        for sub in all_subs:
            status = sub.get('status', 'unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        with col1:
            st.metric("🟢 Active", status_counts.get('active', 0))
        with col2:
            st.metric("🔴 Canceled", status_counts.get('canceled', 0))
        with col3:
            st.metric("⏸️ Incomplete", status_counts.get('incomplete', 0))
        with col4:
            st.metric("📊 Total", len(all_subs))
        
        st.divider()
        
        # Display filtered subscriptions
        for sub in filtered_subs:
            status_emoji = {
                'active': '🟢',
                'canceled': '🔴',
                'incomplete': '⏸️',
                'past_due': '⏰',
                'unpaid': '💰'
            }.get(sub.get('status', 'unknown'), '❓')
            
            st.subheader(f"{status_emoji} {sub['id']}")
            
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"👤 **Customer:** {sub['customer_id']}")
                st.write(f"� **Start Date:** {sub.get('start_date', 'N/A')}")
                st.write(f"🏷️ **Status:** {sub.get('status', 'unknown')}")
            
            with col2:
                st.write(f"� **Price ID:** {sub.get('price_id', 'N/A')}")
                if 'items' in sub and 'data' in sub['items'] and len(sub['items']['data']) > 0:
                    plan = sub['items']['data'][0].get('plan', {})
                    amount = plan.get('amount', 0) / 100
                    interval = plan.get('interval', 'unknown')
                    st.write(f"💰 **Amount:** €{amount:.2f} / {interval}")
                
                if sub.get('canceled_at'):
                    st.write(f"❌ **Canceled:** {sub.get('canceled_at')}")
            
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
    st.header("📈 Business Summary")
    
    # Get data from multiple endpoints
    customers = safe_json("/customers")
    all_subs = safe_json("/subscriptions")
    charges = safe_json("/charges")
    
    if customers and all_subs and charges:
        # Top metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("� Total Customers", len(customers))
        
        with col2:
            active_subs = [s for s in all_subs if s.get('status') == 'active']
            st.metric("📦 Active Subscriptions", len(active_subs))
        
        with col3:
            total_charges = sum([c.get('amount', 0) for c in charges]) / 100
            st.metric("💰 Total Revenue", f"€{total_charges:.2f}")
        
        with col4:
            paid_charges = [c for c in charges if c.get('paid', False)]
            st.metric("✅ Successful Charges", len(paid_charges))
        
        st.divider()
        
        # Monthly Revenue Estimation
        monthly_revenue = 0
        for sub in active_subs:
            if 'items' in sub and 'data' in sub['items'] and len(sub['items']['data']) > 0:
                plan = sub['items']['data'][0].get('plan', {})
                amount = plan.get('amount', 0)
                interval = plan.get('interval', 'month')
                
                # Convert to monthly
                if interval == 'month':
                    monthly_revenue += amount
                elif interval == 'year':
                    monthly_revenue += amount / 12
        
        st.subheader("💹 Estimated Monthly Recurring Revenue")
        st.metric("MRR", f"€{monthly_revenue / 100:.2f}")
        
    else:
        st.error("Unable to load summary data. Check if all endpoints are accessible.")

elif section == "Analytics Dashboard":
    st.header("📊 Analytics Dashboard")
    
    # Get data
    all_subs = safe_json("/subscriptions")
    charges = safe_json("/charges")
    customers = safe_json("/customers")
    
    if all_subs:
        # Subscription Status Pie Chart
        st.subheader("📦 Subscription Status Distribution")
        
        status_counts = {}
        for sub in all_subs:
            status = sub.get('status', 'unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        if status_counts:
            fig_pie = px.pie(
                values=list(status_counts.values()),
                names=list(status_counts.keys()),
                title="Subscription Status Breakdown",
                color_discrete_map={
                    'active': '#28a745',
                    'canceled': '#dc3545', 
                    'incomplete': '#ffc107',
                    'past_due': '#fd7e14',
                    'unpaid': '#6f42c1'
                }
            )
            st.plotly_chart(fig_pie, use_container_width=True)
    
    if charges:
        st.subheader("💰 Revenue Analysis")
        
        # Revenue by Customer
        customer_revenue = {}
        for charge in charges:
            customer_id = charge.get('customer_id', 'unknown')
            amount = charge.get('amount', 0) / 100
            customer_revenue[customer_id] = customer_revenue.get(customer_id, 0) + amount
        
        if customer_revenue:
            # Top 5 customers by revenue
            top_customers = sorted(customer_revenue.items(), key=lambda x: x[1], reverse=True)[:5]
            
            if top_customers:
                customer_ids = [c[0] for c in top_customers]
                revenues = [c[1] for c in top_customers]
                
                fig_bar = px.bar(
                    x=customer_ids,
                    y=revenues,
                    title="Top 5 Customers by Revenue (€)",
                    labels={'x': 'Customer ID', 'y': 'Revenue (€)'}
                )
                fig_bar.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig_bar, use_container_width=True)
        
        # Payment Success Rate
        st.subheader("✅ Payment Success Rate")
        
        total_charges = len(charges)
        paid_charges = len([c for c in charges if c.get('paid', False)])
        success_rate = (paid_charges / total_charges * 100) if total_charges > 0 else 0
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Success Rate", f"{success_rate:.1f}%")
        with col2:
            st.metric("Failed Payments", total_charges - paid_charges)
        
        # Success rate gauge
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=success_rate,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Payment Success Rate (%)"},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkgreen"},
                'steps': [
                    {'range': [0, 50], 'color': "lightgray"},
                    {'range': [50, 80], 'color': "yellow"},
                    {'range': [80, 100], 'color': "lightgreen"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        fig_gauge.update_layout(height=400)
        st.plotly_chart(fig_gauge, use_container_width=True)
