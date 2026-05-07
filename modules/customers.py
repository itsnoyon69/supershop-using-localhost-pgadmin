import streamlit as st
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from datetime import datetime
import plotly.express as px
import pandas as pd
from db import get_conn


def show_customers(df):

    st.markdown("## 👥 Customer Dashboard")

    # ================= RFM =================
    today = datetime.today()

    rfm = df.groupby('customer_id').agg({
        'order_date': lambda x: (today - x.max()).days,
        'order_id': 'count',
        'total_price': 'sum'
    }).reset_index()

    rfm.columns = ['customer_id', 'recency', 'frequency', 'monetary']

    # ================= INCLUDE ALL =================
    cust_df = pd.read_sql("SELECT * FROM customers", get_conn())

    rfm = cust_df[['customer_id']].merge(rfm, on='customer_id', how='left')

    rfm['recency'] = rfm['recency'].fillna(999)
    rfm['frequency'] = rfm['frequency'].fillna(0)
    rfm['monetary'] = rfm['monetary'].fillna(0)

    # ================= CLUSTER =================
    scaler = StandardScaler()
    scaled = scaler.fit_transform(rfm[['recency', 'frequency', 'monetary']])

    kmeans = KMeans(n_clusters=3, random_state=42)
    rfm['cluster'] = kmeans.fit_predict(scaled)

    # ================= SEGMENT =================
    rfm['segment'] = 'Normal'

    rfm.loc[rfm['frequency'] == 0, 'segment'] = 'Inactive'
    rfm.loc[rfm['monetary'] > rfm['monetary'].quantile(0.75), 'segment'] = 'VIP'
    rfm.loc[
        (rfm['frequency'] > rfm['frequency'].mean()) &
        (rfm['segment'] != 'VIP'),
        'segment'
    ] = 'Loyal'

    # ================= KPI =================
    st.subheader("📊 Customer Summary")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("👥 Total", len(rfm))
    col2.metric("👑 VIP", len(rfm[rfm['segment'] == 'VIP']))
    col3.metric("🔁 Loyal", len(rfm[rfm['segment'] == 'Loyal']))
    col4.metric("⚠️ Inactive", len(rfm[rfm['segment'] == 'Inactive']))

    st.markdown("---")

    # ================= VISUAL =================
    st.subheader("📈 Customer Segmentation")

    fig = px.scatter(
        rfm,
        x='frequency',
        y='monetary',
        color='segment',
        size='monetary',
        hover_data=['customer_id'],
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # ================= FILTER =================
    st.subheader("🔍 Filter Customers")

    segment_option = st.selectbox(
        "Select Segment",
        ["All", "VIP", "Loyal", "Normal", "Inactive"]
    )

    if segment_option != "All":
        filtered = rfm[rfm['segment'] == segment_option]
    else:
        filtered = rfm

    # ================= TABLE =================
    st.subheader("📋 Customer List")

    st.dataframe(
        filtered.sort_values(by='monetary', ascending=False)
        [['customer_id', 'recency', 'frequency', 'monetary', 'segment']]
        .head(20),
        use_container_width=True
    )

    st.write("Total:", len(filtered))

    st.markdown("---")

    # ================= CAMPAIGN =================
    st.subheader("🎯 Campaign Manager")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("👑 VIP Campaign"):
            st.success("VIP Offer Running")
            st.write("• 20% Discount")
            st.write("• Premium Access")

    with col2:
        if st.button("🔁 Loyalty Program"):
            st.success("Loyalty Activated")
            st.write("• Reward Points")
            st.write("• Cashback")

    with col3:
        if st.button("🙂 Conversion Offer"):
            st.info("Conversion Campaign")
            st.write("• 10% Discount")
            st.write("• Combo Deals")

    with col4:
        if st.button("⚠️ Reactivation"):
            st.warning("Reactivation Started")
            st.write("• 30% Discount")
            st.write("• Email Campaign")

    st.markdown("---")

    # ================= SMART INSIGHT =================
    st.subheader("🧠 Smart Insight")

    if segment_option == "VIP":
        st.success("👑 Focus on retention & premium services")

    elif segment_option == "Loyal":
        st.success("🔁 Boost repeat purchases with rewards")

    elif segment_option == "Inactive":
        st.warning("⚠️ Need re-engagement campaign")

    elif segment_option == "Normal":
        st.info("🙂 Convert into loyal customers")

    else:
        vip_ratio = len(rfm[rfm['segment'] == 'VIP']) / len(rfm)

        if vip_ratio > 0.2:
            st.success("🔥 Strong high-value customer base")
        else:
            st.warning("⚠️ Need to increase VIP customers")