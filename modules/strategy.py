import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from sklearn.linear_model import LinearRegression


# =========================================================
# STRATEGY SYSTEM
# =========================================================
def show_strategy(df):

    st.markdown("## 🎯 AI Business Strategy")

    # =====================================================
    # DATA PREP
    # =====================================================
    product_df = df.groupby('product_name').agg({
        'quantity': 'sum',
        'total_price': 'sum',
        'order_id': 'nunique',
        'customer_id': 'nunique'
    }).reset_index()

    product_df.columns = [
        'product_name',
        'sales',
        'revenue',
        'orders',
        'customers'
    ]

    # =====================================================
    # PRODUCT SCORE
    # =====================================================
    product_df['sales_score'] = (
        product_df['sales'] /
        product_df['sales'].max()
    ) * 100

    product_df['revenue_score'] = (
        product_df['revenue'] /
        product_df['revenue'].max()
    ) * 100

    product_df['customer_score'] = (
        product_df['customers'] /
        product_df['customers'].max()
    ) * 100

    product_df['strategy_score'] = (
        product_df['sales_score'] * 0.4 +
        product_df['revenue_score'] * 0.4 +
        product_df['customer_score'] * 0.2
    )

    # =====================================================
    # STATUS
    # =====================================================
    def product_status(score):

        if score >= 75:
            return "🔥 Growth Opportunity"

        elif score >= 45:
            return "📈 Stable"

        else:
            return "⚠️ Risk Product"

    product_df['status'] = product_df[
        'strategy_score'
    ].apply(product_status)

    # =====================================================
    # OVERVIEW
    # =====================================================
    st.subheader("📊 Strategy Overview")

    top_product = product_df.sort_values(
        by='strategy_score',
        ascending=False
    ).iloc[0]

    weak_products = product_df[
        product_df['status'] ==
        "⚠️ Risk Product"
    ]

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "🔥 Best Product",
        top_product['product_name']
    )

    col2.metric(
        "📈 Top Score",
        f"{top_product['strategy_score']:.1f}"
    )

    col3.metric(
        "⚠️ Risk Products",
        len(weak_products)
    )

    st.markdown("---")

    # =====================================================
    # PRODUCT STRATEGY
    # =====================================================
    st.subheader("📦 Product Strategy")

    selected_product = st.selectbox(
        "Select Product",
        product_df['product_name'].unique(),
        key="strategy_product"
    )

    row = product_df[
        product_df['product_name'] ==
        selected_product
    ].iloc[0]

    # =====================================================
    # PRODUCT METRICS
    # =====================================================
    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Sales",
        int(row['sales'])
    )

    col2.metric(
        "Revenue",
        f"{row['revenue']:.0f}"
    )

    col3.metric(
        "Strategy",
        row['status']
    )

    st.markdown("---")

    # =====================================================
    # AI STRATEGY
    # =====================================================
    if row['strategy_score'] >= 75:

        st.success(f"""
        🔥 {selected_product} has strong growth potential.

        Recommended Strategy:
        • Increase stock
        • Push marketing campaigns
        • Highlight in homepage
        • Create combo offers
        """)

    elif row['strategy_score'] >= 45:

        st.info(f"""
        📈 {selected_product} is stable.

        Recommended Strategy:
        • Monitor performance
        • Improve promotions
        • Test bundle strategy
        """)

    else:

        st.warning(f"""
        ⚠️ {selected_product} is risky.

        Recommended Strategy:
        • Apply discounts
        • Reduce inventory
        • Bundle with top products
        """)

    st.markdown("---")

    # =====================================================
    # PRODUCT SCORE GRAPH
    # =====================================================
    st.subheader("📈 Product Analysis")

    graph_df = pd.DataFrame({
        'Metric': [
            'Sales',
            'Revenue',
            'Customers'
        ],
        'Score': [
            row['sales_score'],
            row['revenue_score'],
            row['customer_score']
        ]
    })

    fig = px.bar(
        graph_df,
        x='Metric',
        y='Score',
        title="Product Strategy Analysis"
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        key="strategy_graph"
    )

    st.markdown("---")

    # =====================================================
    # CUSTOMER STRATEGY
    # =====================================================
    st.subheader("👥 Customer Strategy")

    customer_df = df.groupby('customer_id').agg({
        'order_id': 'nunique',
        'quantity': 'sum',
        'total_price': 'sum',
        'order_date': 'max'
    }).reset_index()

    customer_df.columns = [
        'customer_id',
        'orders',
        'items',
        'spending',
        'last_order'
    ]

    # inactivity
    today = df['order_date'].max()

    customer_df['inactive_days'] = (
        today - customer_df['last_order']
    ).dt.days

    # score
    customer_df['customer_score'] = (
        (
            customer_df['orders'] /
            customer_df['orders'].max()
        ) * 30
        +
        (
            customer_df['spending'] /
            customer_df['spending'].max()
        ) * 50
        +
        (
            1 -
            (
                customer_df['inactive_days'] /
                customer_df['inactive_days'].max()
            )
        ) * 20
    )

    # =====================================================
    # SELECT CUSTOMER
    # =====================================================
    selected_customer = st.selectbox(
        "Select Customer",
        customer_df['customer_id'].unique(),
        key="strategy_customer"
    )

    cust = customer_df[
        customer_df['customer_id'] ==
        selected_customer
    ].iloc[0]

    # =====================================================
    # CUSTOMER TYPE
    # =====================================================
    if cust['customer_score'] >= 75:

        customer_status = "💎 High Value"

        recommendation = """
        • Send loyalty rewards
        • Offer premium products
        • Give early access offers
        """

    elif cust['customer_score'] >= 45:

        customer_status = "📈 Moderate"

        recommendation = """
        • Personalized offers
        • Product recommendations
        • Engagement campaigns
        """

    else:

        customer_status = "⚠️ At Risk"

        recommendation = """
        • Reactivation discount
        • Retarget campaigns
        • Follow-up promotions
        """

    # =====================================================
    # CUSTOMER METRICS
    # =====================================================
    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Customer Score",
        f"{cust['customer_score']:.1f}"
    )

    col2.metric(
        "Total Spending",
        f"{cust['spending']:.0f}"
    )

    col3.metric(
        "Status",
        customer_status
    )

    st.markdown("---")

    # =====================================================
    # CUSTOMER STRATEGY AI
    # =====================================================
    st.success(f"""
    👤 Customer:
    {selected_customer}

    Recommended Strategy:
    {recommendation}
    """)

    st.markdown("---")

    # =====================================================
    # REVENUE STRATEGY
    # =====================================================
    st.subheader("💰 Revenue Strategy")

    revenue_df = df.groupby('order_date').agg({
        'total_price': 'sum'
    }).reset_index()

    revenue_df['day'] = range(len(revenue_df))

    X = revenue_df[['day']]
    y = revenue_df['total_price']

    model = LinearRegression()

    model.fit(X, y)

    future_days = st.slider(
        "Forecast Days",
        7,
        180,
        30,
        key="strategy_forecast_days"
    )

    future_revenue = model.predict(
        [[len(revenue_df) + future_days]]
    )[0]

    current_avg = revenue_df[
        'total_price'
    ].mean()

    growth = (
        (future_revenue - current_avg)
        / current_avg
    ) * 100

    # =====================================================
    # REVENUE METRICS
    # =====================================================
    col1, col2 = st.columns(2)

    col1.metric(
        "Predicted Revenue",
        f"{future_revenue:.0f}"
    )

    col2.metric(
        "Growth Forecast",
        f"{growth:.2f}%"
    )

    st.markdown("---")

    # =====================================================
    # REVENUE STRATEGY AI
    # =====================================================
    if growth > 15:

        st.success("""
        🚀 Strong Growth Expected

        Strategy:
        • Increase inventory
        • Increase marketing budget
        • Focus on best-selling products
        """)

    elif growth > 0:

        st.info("""
        📈 Stable Revenue Trend

        Strategy:
        • Maintain operations
        • Improve customer retention
        """)

    else:

        st.warning("""
        📉 Revenue Risk Detected

        Strategy:
        • Reduce weak inventory
        • Run discount campaigns
        • Optimize spending
        """)

    # =====================================================
    # REVENUE GRAPH
    # =====================================================
    graph_data = pd.DataFrame({
        'Type': [
            'Current Revenue',
            'Future Revenue'
        ],
        'Revenue': [
            current_avg,
            future_revenue
        ]
    })

    fig2 = px.bar(
        graph_data,
        x='Type',
        y='Revenue',
        title="Revenue Forecast"
    )

    st.plotly_chart(
        fig2,
        use_container_width=True,
        key="revenue_strategy_graph"
    )

    st.markdown("---")

    # =====================================================
    # FINAL STRATEGY
    # =====================================================
    st.subheader("🚀 Final Business Strategy")

    st.success(f"""
    🔥 Focus Product:
    {top_product['product_name']}

    📈 Revenue Growth Forecast:
    {growth:.2f}%

    🎯 Recommended Actions:
    • Increase focus on top products
    • Retain valuable customers
    • Reduce risk inventory
    • Improve marketing efficiency
    """)