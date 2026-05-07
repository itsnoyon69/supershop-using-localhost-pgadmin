import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

from prophet import Prophet
from sklearn.metrics.pairwise import cosine_similarity


# ================= 1. FORECAST GRAPH =================
def forecast_graph(data, forecast):

    # smooth line
    forecast['smooth'] = forecast['yhat'].rolling(7).mean()

    fig = go.Figure()

    # Actual
    fig.add_trace(go.Scatter(
        x=data['ds'],
        y=data['y'],
        name="Actual",
        line=dict(width=2)
    ))

    # Forecast
    fig.add_trace(go.Scatter(
        x=forecast['ds'],
        y=forecast['smooth'],
        name="Forecast",
        line=dict(width=3)
    ))

    # Upper range
    fig.add_trace(go.Scatter(
        x=forecast['ds'],
        y=forecast['yhat_upper'],
        line=dict(width=0),
        showlegend=False
    ))

    # Lower range
    fig.add_trace(go.Scatter(
        x=forecast['ds'],
        y=forecast['yhat_lower'],
        fill='tonexty',
        name='Confidence Range',
        opacity=0.2
    ))

    fig.update_layout(
        template="plotly_white",
        height=500
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        key="forecast_chart"
    )


# ================= 2. GROWTH + CONFIDENCE =================
def growth_confidence(forecast, days):

    # ---------- Growth ----------
    recent = forecast['yhat'].tail(7).mean()

    past = forecast['yhat'].iloc[
           -(days + 7):-days
           ].mean()

    if pd.isna(past) or past == 0:
        growth = 0

    else:
        growth = ((recent - past) / past) * 100

    # ---------- Dynamic Confidence ----------
    future_data = forecast.tail(days)

    avg_pred = future_data['yhat'].mean()

    uncertainty = (
        future_data['yhat_upper'] -
        future_data['yhat_lower']
    ).mean()

    if avg_pred == 0 or pd.isna(avg_pred):

        confidence = 50

    else:

        relative = uncertainty / (
            abs(avg_pred) + uncertainty
        )

        confidence = (1 - relative) * 100

    confidence = round(confidence, 1)

    # realistic range
    confidence = max(35, min(95, confidence))

    # ---------- Stability ----------
    first_range = (
        future_data['yhat_upper'] -
        future_data['yhat_lower']
    ).head(5).mean()

    last_range = (
        future_data['yhat_upper'] -
        future_data['yhat_lower']
    ).tail(5).mean()

    diff = abs(last_range - first_range)

    if diff < 5:
        stability = "📉 Stable"

    elif diff < 15:
        stability = "📊 Moderate"

    else:
        stability = "📈 Uncertain"

    return growth, confidence, stability


# ================= 3. FUTURE SUMMARY =================
def future_summary(forecast, days):

    st.subheader("🔮 Future Prediction")

    future_data = forecast.tail(days)

    avg_val = future_data['yhat'].mean()
    max_val = future_data['yhat_upper'].max()
    min_val = future_data['yhat_lower'].min()

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "📊 Avg Future",
        f"{avg_val:.1f}"
    )

    col2.metric(
        "🚀 Best Case",
        f"{max_val:.1f}"
    )

    col3.metric(
        "⚠️ Worst Case",
        f"{min_val:.1f}"
    )


# ================= 4. SMART STOCK RISK =================
def stock_risk(df, forecast, days):

    st.subheader("⚠️ Smart Stock Risk")

    future_avg = forecast['yhat'].tail(days).mean()

    prod = df.groupby('product_name')['quantity'] \
        .sum() \
        .reset_index()

    avg_sales = prod['quantity'].mean()

    # low stock
    low_stock = prod[
        prod['quantity'] < avg_sales
    ]

    # over stock
    overstock = prod[
        prod['quantity'] > (avg_sales * 2)
    ]

    col1, col2 = st.columns(2)

    # ---------- LOW STOCK ----------
    with col1:

        st.write("🔴 Stock-Out Risk")

        if len(low_stock) > 0:

            for row in low_stock.head(5).itertuples():

                st.warning(
                    f"{row.product_name} may run out soon"
                )

        else:
            st.success("No stock risk detected")

    # ---------- OVER STOCK ----------
    with col2:

        st.write("🟡 Overstock Alert")

        if len(overstock) > 0:

            for row in overstock.head(5).itertuples():

                st.info(
                    f"{row.product_name} has excess stock"
                )

        else:
            st.success("No overstock issue")


# ================= 5. CUSTOMER PRODUCT ML =================
def customer_product_prediction(df):

    st.subheader("🛒 Future Customer Product Prediction")

    # user-product matrix
    user_product = df.pivot_table(
        index='customer_id',
        columns='product_name',
        values='quantity',
        aggfunc='sum',
        fill_value=0
    )

    # similarity matrix
    similarity = cosine_similarity(user_product)

    similarity_df = pd.DataFrame(
        similarity,
        index=user_product.index,
        columns=user_product.index
    )

    # customer select
    selected_customer = st.selectbox(
        "Select Customer",
        user_product.index,
        key="customer_prediction"
    )

    # similar customers
    similar_users = similarity_df[selected_customer] \
        .sort_values(ascending=False)

    similar_users = similar_users.iloc[1:6]

    # already purchased
    bought_products = set(
        user_product.loc[selected_customer]
        [user_product.loc[selected_customer] > 0]
        .index
    )

    # recommendations
    recommended_products = {}

    for sim_user in similar_users.index:

        sim_products = user_product.loc[sim_user]

        for product, qty in sim_products.items():

            if qty > 0 and product not in bought_products:

                if product not in recommended_products:

                    recommended_products[product] = qty

                else:

                    recommended_products[product] += qty

    # no recommendation
    if len(recommended_products) == 0:

        st.info("No prediction available")

        return

    # dataframe
    rec_df = pd.DataFrame(
        recommended_products.items(),
        columns=['Product', 'Prediction Score']
    )

    rec_df = rec_df.sort_values(
        by='Prediction Score',
        ascending=False
    ).head(5)

    # layout
    col1, col2 = st.columns([1, 2])

    # table
    with col1:

        st.dataframe(
            rec_df,
            use_container_width=True
        )

    # graph
    with col2:

        fig = px.bar(
            rec_df,
            x='Product',
            y='Prediction Score',
            title="Future Purchase Prediction"
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            key="future_prediction_chart"
        )

    # insight
    top_product = rec_df.iloc[0]['Product']

    st.success(
        f"🎯 Customer {selected_customer} is likely to buy '{top_product}' next"
    )


# ================= MAIN FUNCTION =================
def show_forecast(df):

    st.markdown("## 🔮 Forecast Dashboard")

    # ---------- SETTINGS ----------
    col1, col2 = st.columns(2)

    with col1:

        days = st.slider(
            "Forecast Days",
            7,
            90,
            30,
            key="forecast_days"
        )

    with col2:

        metric = st.selectbox(
            "Forecast Metric",
            ["quantity", "total_price"],
            key="forecast_metric"
        )

    # ---------- DATA ----------
    data = df.groupby('order_date')[metric] \
        .sum() \
        .reset_index()

    data.columns = ['ds', 'y']

    # ---------- MODEL ----------
    model = Prophet()

    model.fit(data)

    future = model.make_future_dataframe(
        periods=days
    )

    forecast = model.predict(future)

    # ================= FORECAST GRAPH =================
    st.subheader("📈 Forecast Graph")

    forecast_graph(data, forecast)

    st.markdown("---")

    # ================= GROWTH =================
    st.subheader("📊 Growth & Confidence")

    growth, confidence, stability = growth_confidence(
        forecast,
        days
    )

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Growth %",
        f"{growth:.2f}%"
    )

    col2.metric(
        "Confidence %",
        f"{confidence:.1f}%"
    )

    col3.write(stability)

    st.markdown("---")

    # ================= FUTURE =================
    future_summary(forecast, days)

    st.markdown("---")

    # ================= STOCK =================
    stock_risk(df, forecast, days)

    st.markdown("---")

    # ================= CUSTOMER PRODUCT AI =================
    customer_product_prediction(df)