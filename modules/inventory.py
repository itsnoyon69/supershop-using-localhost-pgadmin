import streamlit as st
import pandas as pd
import plotly.express as px

def show_inventory(df):

    st.markdown("## 📦 Inventory Management (Stock)")

    # ================= DATA =================
    stock = df.groupby([
        'product_name',
        'size'
    ])['quantity'].sum().reset_index()

    low_stock = stock[
        stock['quantity'] < 10
    ]

    high_stock = stock[
        stock['quantity'] > 80
    ]

    size_stock = df.groupby(
        'size'
    )['quantity'].sum().reset_index()

    # ================= KPI =================
    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "📦 Total Stock",
        int(stock['quantity'].sum())
    )

    col2.metric(
        "🛍 Products",
        stock['product_name'].nunique()
    )

    col3.metric(
        "🔴 Low Stock",
        len(low_stock)
    )

    col4.metric(
        "🟡 Overstock",
        len(high_stock)
    )

    st.markdown("---")

    # ================= ALERT =================
    st.subheader("⚠️ Stock Alerts")

    col1, col2 = st.columns(2)

    # =================================================
    # LOW STOCK
    # =================================================
    with col1:

        st.write("🔴 Low Stock")

        if len(low_stock) == 0:

            st.success(
                "No low stock issues"
            )

        else:

            for r in low_stock.itertuples():

                st.error(
                    f"{r.product_name} ({r.size}) → {r.quantity}"
                )

    # =================================================
    # OVER STOCK
    # =================================================
    with col2:

        st.write("🟡 Overstock")

        if len(high_stock) == 0:

            st.info(
                "No overstock issues"
            )

        else:

            for r in high_stock.itertuples():

                st.warning(
                    f"{r.product_name} ({r.size}) → {r.quantity}"
                )

    st.markdown("---")

    # ================= SIZE STOCK =================
    st.subheader("📏 Size Stock Distribution")

    fig1 = px.bar(
        size_stock,
        x='size',
        y='quantity',
        title="Size Stock"
    )

    st.plotly_chart(
        fig1,
        use_container_width=True,
        key="inv_size"
    )

    st.markdown("---")

    # ================= PRODUCT STOCK =================
    st.subheader("📦 Product Stock View")

    # =================================================
    # ALIGNMENT FIX
    # =================================================
    col1, col2 = st.columns([3, 1])

    with col1:

        product_options = [
                              "Select Product"
                          ] + list(
            df['product_name']
            .dropna()
            .unique()
        )

        selected_product = st.selectbox(
            "Select Product",
            product_options,
            index=0,
            key="inv_selectbox"
        )

    with col2:

        st.write("")
        st.write("")

        show_btn = st.button(
            "🔍 Show Product Stock",
            use_container_width=True
        )

    # =================================================
    # SHOW GRAPH
    # =================================================
    if show_btn:

        if selected_product == "Select Product":

            st.warning("""
            Please select a product
            """)

        else:

            product_stock = stock[
                stock['product_name']
                == selected_product
            ]

            fig2 = px.bar(
                product_stock,
                x='size',
                y='quantity',
                title=f"{selected_product} Stock by Size",
                color='quantity'
            )

            st.plotly_chart(
                fig2,
                use_container_width=True,
                key="inv_product"
            )

            # =================================================
            # STOCK INSIGHT
            # =================================================
            total_stock = product_stock[
                'quantity'
            ].sum()

            avg_stock = stock[
                'quantity'
            ].mean()

            st.markdown("---")

            st.subheader("🧠 Product Stock Insight")

            if total_stock < avg_stock:

                st.error(f"""
                ⚠️ {selected_product} stock is low.

                Suggested Action:
                • Restock soon
                • Monitor fast-selling sizes
                """)

            elif total_stock > avg_stock * 2:

                st.warning(f"""
                🟡 {selected_product} has high stock.

                Suggested Action:
                • Run discounts
                • Create combo offers
                • Clear excess inventory
                """)

            else:

                st.success(f"""
                ✅ {selected_product} stock level is balanced.
                """)

    st.markdown("---")

    # ================= ACTION =================
    st.subheader("🎯 Suggested Actions")

    if len(low_stock) > 0:

        st.write("📦 Restock Needed:")

        for r in low_stock.itertuples():

            st.write(
                f"→ {r.product_name} ({r.size})"
            )

    if len(high_stock) > 0:

        st.write("💸 Discount / Clear Stock:")

        for r in high_stock.itertuples():

            st.write(
                f"→ {r.product_name} ({r.size})"
            )

    if (
        len(low_stock) == 0
        and
        len(high_stock) == 0
    ):

        st.success("""
        ✅ Stock levels are balanced
        """)