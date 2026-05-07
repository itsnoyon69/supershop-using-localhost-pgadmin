import streamlit as st
import pandas as pd
import plotly.express as px

def show_products(df):

    st.markdown("## 📦 Product Analytics (Demand)")

    # ================= DATA =================
    prod = df.groupby('product_name').agg({
        'quantity': 'sum',
        'total_price': 'sum'
    }).reset_index().sort_values(
        by='quantity',
        ascending=False
    )

    size_df = df.groupby([
        'product_name',
        'size'
    ])['quantity'].sum().reset_index()

    size_total = df.groupby(
        'size'
    )['quantity'].sum().reset_index().sort_values(
        by='quantity',
        ascending=False
    )

    # ================= KPI =================
    col1, col2, col3 = st.columns(3)

    col1.metric(
        "📦 Total Products",
        prod['product_name'].nunique()
    )

    col2.metric(
        "🔥 Best Seller",
        prod.iloc[0]['product_name']
    )

    col3.metric(
        "⚠️ Low Seller",
        prod.iloc[-1]['product_name']
    )

    st.markdown("---")

    # ================= SALES CHART =================
    st.subheader("📈 Top Selling Products")

    fig1 = px.bar(
        prod.head(10),
        x='product_name',
        y='quantity',
        title="Top Products by Sales"
    )

    st.plotly_chart(
        fig1,
        use_container_width=True,
        key="prod_bar"
    )

    st.markdown("---")

    # ================= LOW SELLING =================
    st.subheader("⚠️ Low Selling Products")

    low_products = prod.sort_values(
        by='quantity',
        ascending=True
    ).head(10)

    fig_low = px.bar(
        low_products,
        x='product_name',
        y='quantity',
        title="Low Selling Products",
        color='quantity'
    )

    st.plotly_chart(
        fig_low,
        use_container_width=True,
        key="low_selling_chart"
    )

    st.markdown("---")

    # ================= SIZE DEMAND =================
    st.subheader("📏 Size Demand")

    col1, col2 = st.columns(2)

    # =================================================
    # OVERALL SIZE
    # =================================================
    with col1:

        fig2 = px.bar(
            size_total,
            x='size',
            y='quantity',
            title="Overall Size Demand"
        )

        st.plotly_chart(
            fig2,
            use_container_width=True,
            key="size_total"
        )

    # =================================================
    # PRODUCT SIZE
    # =================================================
    with col2:

        # blank option
        product_options = ["Select Product"] + list(
            df['product_name']
            .dropna()
            .unique()
        )

        selected_product = st.selectbox(
            "Select Product",
            product_options,
            index=0,
            key="prod_selectbox"
        )

        # button
        if st.button(
            "🔍 Show Product Size Demand"
        ):

            if selected_product == "Select Product":

                st.warning("""
                Please select a product
                """)

            else:

                product_size = size_df[
                    size_df['product_name']
                    == selected_product
                ]

                fig3 = px.bar(
                    product_size,
                    x='size',
                    y='quantity',
                    title=f"{selected_product} Size Demand"
                )

                st.plotly_chart(
                    fig3,
                    use_container_width=True,
                    key="size_product"
                )

    st.markdown("---")

    # ================= INSIGHT =================
    st.subheader("🧠 Product Insight")

    top_product = prod.iloc[0]['product_name']

    low_product = prod.iloc[-1]['product_name']

    st.success(
        f"🔥 Best Selling Product: {top_product}"
    )

    st.warning(
        f"⚠️ Low Performing Product: {low_product}"
    )

    st.info(
        f"🎯 Strategy: Promote '{low_product}' or bundle with '{top_product}'"
    )