import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import random

from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler


# =========================================================
# BUSINESS OPTIMIZATION ENGINE
# =========================================================
def show_combo_engine(df):

    st.markdown("## 🤖 Business Optimization Engine")

    # =====================================================
    # SESSION STATE
    # =====================================================
    if "combo_history" not in st.session_state:
        st.session_state.combo_history = []

    if "discount_history" not in st.session_state:
        st.session_state.discount_history = []

    if "ai_history" not in st.session_state:
        st.session_state.ai_history = []

    if "ai_combo_result" not in st.session_state:
        st.session_state.ai_combo_result = None

    if "ai_discount_result" not in st.session_state:
        st.session_state.ai_discount_result = None

    # =====================================================
    # PRODUCT DATA
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
    # AVG PRICE
    # =====================================================
    product_df['avg_price'] = (
        product_df['revenue'] /
        product_df['sales']
    )

    product_df = product_df.replace(
        [np.inf, -np.inf],
        0
    ).fillna(0)

    # =====================================================
    # ML FEATURES
    # =====================================================
    features = product_df[[
        'sales',
        'revenue',
        'orders',
        'customers'
    ]]

    scaler = StandardScaler()

    scaled = scaler.fit_transform(
        features
    )

    # =====================================================
    # KMEANS MODEL
    # =====================================================
    model = KMeans(
        n_clusters=3,
        random_state=42,
        n_init=10
    )

    product_df['cluster'] = model.fit_predict(
        scaled
    )

    # =====================================================
    # LABELS
    # =====================================================
    cluster_sales = product_df.groupby(
        'cluster'
    )['sales'].mean()

    high_cluster = cluster_sales.idxmax()
    low_cluster = cluster_sales.idxmin()

    def cluster_label(c):

        if c == high_cluster:
            return "🔥 High Demand"

        elif c == low_cluster:
            return "⚠️ Weak Demand"

        else:
            return "📈 Moderate"

    product_df['status'] = product_df[
        'cluster'
    ].apply(cluster_label)

    # =====================================================
    # SMART COMBO MODEL
    # =====================================================
    def calculate_combo_metrics(
            p1,
            p2,
            combo_discount
    ):

        # =============================================
        # SALES SCORE
        # =============================================
        weak_score = (
                             p1['sales'] /
                             product_df['sales'].max()
                     ) * 100

        strong_score = (
                               p2['sales'] /
                               product_df['sales'].max()
                       ) * 100

        # =============================================
        # DYNAMIC SUCCESS SCORE
        # =============================================
        weak_factor = (
                (100 - weak_score) * 0.45
        )

        strong_factor = (
                strong_score * 0.35
        )

        # =============================================
        # DISCOUNT EFFECT
        # =============================================
        if combo_discount <= 10:

            discount_factor = 8

        elif combo_discount <= 20:

            discount_factor = 18

        elif combo_discount <= 30:

            discount_factor = 25

        elif combo_discount <= 40:

            discount_factor = 10

        else:

            discount_factor = -15

        # =============================================
        # MARKET VARIATION
        # =============================================
        market_variation = random.uniform(
            -8,
            8
        )

        # =============================================
        # DYNAMIC COMBO SCORE
        # =============================================

        # low product priority
        low_product_factor = (
                (
                        100 - weak_score
                ) * 0.55
        )

        # strong product support
        strong_product_factor = (
                strong_score * 0.30
        )

        # revenue factor
        revenue_factor = (
                                 (
                                         p1['revenue'] +
                                         p2['revenue']
                                 ) /
                                 product_df['revenue'].max()
                         ) * 12

        # random market behaviour
        market_dynamic = random.uniform(
            -15,
            15
        )

        # final score
        combo_score = (

                low_product_factor +

                strong_product_factor +

                revenue_factor +

                discount_factor +

                market_dynamic
        )

        combo_score = max(
            random.randint(20, 35),
            min(
                random.randint(85, 98),
                combo_score
            )
        )

        # =============================================
        # GROWTH
        # =============================================
        expected_growth = (
                combo_score * 0.22
        )

        expected_growth = min(
            expected_growth,
            45
        )

        # =============================================
        # PRICE
        # =============================================
        price1 = p1['avg_price']
        price2 = p2['avg_price']

        original_price = (
                price1 + price2
        )

        combo_price = (
                original_price *
                (
                        1 -
                        combo_discount / 100
                )
        )

        # =============================================
        # PROFIT
        # =============================================
        estimated_cost = (
                original_price * 0.72
        )

        estimated_profit = (
                combo_price -
                estimated_cost
        )

        # =============================================
        # REVENUE
        # =============================================
        current_revenue = (
                p1['revenue'] +
                p2['revenue']
        )

        predicted_revenue = (
                current_revenue *
                (
                        1 +
                        expected_growth / 100
                )
        )

        return (

            round(combo_score, 1),

            round(expected_growth, 1),

            round(original_price, 0),

            round(combo_price, 0),

            round(predicted_revenue, 0),

            round(estimated_profit, 0)
        )

    # =====================================================
    # TABS
    # =====================================================
    tab1, tab2, tab3 = st.tabs([
        "🎁 Combo Simulator",
        "💸 Discount Simulator",
        "🤖 AI Suggestion"
    ])

    # =====================================================
    # COMBO TAB
    # =====================================================
    with tab1:

        st.subheader(
            "🎁 Smart Combo Simulator"
        )

        product_options = [
            "Select Product"
        ] + list(
            product_df[
                'product_name'
            ].unique()
        )

        col1, col2 = st.columns(2)

        with col1:

            product1 = st.selectbox(
                "Select Product A",
                product_options,
                index=0
            )

        with col2:

            product2 = st.selectbox(
                "Select Product B",
                product_options,
                index=0
            )

        combo_discount = st.number_input(
            "Apply Combo Discount %",
            min_value=1,
            max_value=100,
            value=15,
            step=1
        )

        confirm_combo = st.button(
            "🚀 Create Combo Prediction",
            use_container_width=True
        )

        if confirm_combo:

            if (
                product1 == "Select Product"
                or
                product2 == "Select Product"
            ):

                st.warning("""
                Please select both products
                """)

            elif product1 == product2:

                st.error("""
                Please select different products
                """)

            else:

                p1 = product_df[
                    product_df['product_name']
                    == product1
                ].iloc[0]

                p2 = product_df[
                    product_df['product_name']
                    == product2
                ].iloc[0]

                (
                    combo_score,
                    expected_growth,
                    original_price,
                    combo_price,
                    predicted_revenue,
                    estimated_profit
                ) = calculate_combo_metrics(
                    p1,
                    p2,
                    combo_discount
                )

                # =========================================
                # OUTPUT
                # =========================================
                c1, c2, c3, c4 = st.columns(4)

                c1.metric(
                    "Success Rate",
                    f"{combo_score:.1f}%"
                )

                c2.metric(
                    "Expected Growth",
                    f"{expected_growth:.1f}%"
                )

                c3.metric(
                    "Original Price",
                    f"{original_price:.0f}"
                )

                c4.metric(
                    "Combo Price",
                    f"{combo_price:.0f}"
                )

                st.markdown("---")

                x1, x2 = st.columns(2)

                x1.metric(
                    "Predicted Revenue",
                    f"{predicted_revenue:.0f}"
                )

                x2.metric(
                    "Estimated Profit",
                    f"{estimated_profit:.0f}"
                )

                st.markdown("---")

                # =========================================
                # RESULT
                # =========================================
                if estimated_profit <= 0:

                    st.error(f"""
                    ❌ Loss Risk Detected

                    {combo_discount}% discount is too high.
                    Profit may become negative.
                    """)

                elif combo_discount > 35:

                    st.warning(f"""
                    ⚠️ High Discount Warning

                    Revenue may increase,
                    but profit becomes risky.
                    """)

                elif combo_score >= 80:

                    st.success(f"""
                    🔥 Best Combo Strategy

                    • Weak product sales may grow
                    • Discount range looks perfect
                    • Strong revenue potential
                    """)

                elif combo_score >= 60:

                    st.info("""
                    📈 Moderate Combo Potential
                    """)

                else:

                    st.error("""
                    ⚠️ Weak Combo Match
                    """)

                # =========================================
                # SAVE
                # =========================================
                if st.button(
                    "💾 Save Combo Strategy"
                ):

                    combo_data = {

                        "Type":
                            "Combo",

                        "Product A":
                            product1,

                        "Product B":
                            product2,

                        "Discount":
                            f"{combo_discount}%",

                        "Success Rate":
                            combo_score,

                        "Growth":
                            expected_growth,

                        "Revenue":
                            predicted_revenue,

                        "Profit":
                            estimated_profit
                    }

                    st.session_state.combo_history.append(
                        combo_data
                    )

                    st.success("""
                    ✅ Combo saved
                    """)

                # =========================================
                # GRAPH
                # =========================================
                graph_df = pd.DataFrame({

                    'Type': [
                        'Original Price',
                        'Combo Price'
                    ],

                    'Price': [
                        original_price,
                        combo_price
                    ]
                })

                fig = px.bar(
                    graph_df,
                    x='Type',
                    y='Price',
                    title="Combo Price Comparison"
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

    # =====================================================
    # DISCOUNT TAB
    # =====================================================
    with tab2:

        st.subheader(
            "💸 Smart Discount Simulator"
        )

        weak_only = product_df[
            product_df['status']
            ==
            "⚠️ Weak Demand"
        ]

        discount_options = [
            "Select Product"
        ] + list(
            weak_only[
                'product_name'
            ].unique()
        )

        selected_product = st.selectbox(
            "Select Weak Product",
            discount_options,
            index=0
        )

        discount = st.number_input(
            "Apply Discount %",
            min_value=1,
            max_value=100,
            value=15,
            step=1
        )

        run_discount = st.button(
            "🚀 Create Discount Prediction",
            use_container_width=True
        )

        if run_discount:

            if selected_product == "Select Product":

                st.warning("""
                Please select a product
                """)

            else:

                row = weak_only[
                    weak_only['product_name']
                    ==
                    selected_product
                ].iloc[0]

                current_sales = row[
                    'sales'
                ]

                current_revenue = row[
                    'revenue'
                ]

                # =========================================
                # SMART DISCOUNT EFFECT
                # =========================================
                if discount <= 10:

                    demand_boost = 10

                elif discount <= 20:

                    demand_boost = 22

                elif discount <= 30:

                    demand_boost = 28

                elif discount <= 40:

                    demand_boost = 15

                elif discount <= 50:

                    demand_boost = 5

                else:

                    demand_boost = -15

                future_sales = (
                    current_sales *
                    (
                        1 +
                        demand_boost / 100
                    )
                )

                discounted_revenue = (
                    current_revenue *
                    (
                        1 -
                        discount / 100
                    )
                )

                future_revenue = (
                    discounted_revenue *
                    (
                        1 +
                        demand_boost / 100
                    )
                )

                revenue_change = (
                    (
                        future_revenue -
                        current_revenue
                    )
                    /
                    current_revenue
                ) * 100

                # =========================================
                # PROFIT
                # =========================================
                estimated_cost = (
                    current_revenue * 0.72
                )

                estimated_profit = (
                    future_revenue -
                    estimated_cost
                )

                success_rate = (
                    60 +
                    demand_boost
                )

                success_rate = min(
                    success_rate,
                    95
                )

                # =========================================
                # OUTPUT
                # =========================================
                d1, d2, d3, d4 = st.columns(4)

                d1.metric(
                    "Success Rate",
                    f"{success_rate:.1f}%"
                )

                d2.metric(
                    "Future Sales",
                    f"{future_sales:.0f}"
                )

                d3.metric(
                    "Revenue Impact",
                    f"{revenue_change:.2f}%"
                )

                d4.metric(
                    "Demand Boost",
                    f"{demand_boost:.1f}%"
                )

                st.markdown("---")

                p1, p2 = st.columns(2)

                p1.metric(
                    "Predicted Revenue",
                    f"{future_revenue:.0f}"
                )

                p2.metric(
                    "Estimated Profit",
                    f"{estimated_profit:.0f}"
                )

                st.markdown("---")

                if estimated_profit <= 0:

                    st.error("""
                    ❌ Loss Risk Detected
                    """)

                elif discount > 40:

                    st.warning("""
                    ⚠️ Discount Too High
                    Profit margin decreasing
                    """)

                elif revenue_change > 10:

                    st.success("""
                    🚀 Strong Discount Strategy
                    """)

                elif revenue_change > 0:

                    st.info("""
                    📈 Moderate Discount Strategy
                    """)

                else:

                    st.error("""
                    ⚠️ Weak Discount Strategy
                    """)

                # =========================================
                # SAVE
                # =========================================
                if st.button(
                    "💾 Save Discount Strategy"
                ):

                    discount_data = {

                        "Type":
                            "Discount",

                        "Product":
                            selected_product,

                        "Discount":
                            f"{discount}%",

                        "Success Rate":
                            round(success_rate, 1),

                        "Revenue":
                            round(future_revenue, 0),

                        "Profit":
                            round(estimated_profit, 0)
                    }

                    st.session_state.discount_history.append(
                        discount_data
                    )

                    st.success("""
                    ✅ Discount strategy saved
                    """)

    # =====================================================
    # AI TAB
    # =====================================================
    with tab3:

        st.subheader(
            "🤖 AI Combo + Discount Suggestion"
        )

        # =================================================
        # =================================================
        # =================================================
        # AI COMBO
        # =================================================
        if st.button(
                "🎲 Generate AI Combo"
        ):

            # =============================================
            # PRODUCT GROUP
            # =============================================
            weak_products = product_df[
                product_df['status']
                ==
                "⚠️ Weak Demand"
                ]

            moderate_products = product_df[
                product_df['status']
                ==
                "📈 Moderate"
                ]

            strong_products = product_df[
                product_df['status']
                ==
                "🔥 High Demand"
                ]

            # =============================================
            # RANDOM STRATEGY TYPE
            # =============================================
            strategy_type = random.choice([
                "weak_strong",
                "weak_moderate",
                "moderate_strong"
            ])

            # =============================================
            # SELECT PRODUCTS
            # =============================================
            if strategy_type == "weak_strong":

                weak = weak_products.sample(
                    n=1
                ).iloc[0]

                strong = strong_products.sample(
                    n=1
                ).iloc[0]

            elif strategy_type == "weak_moderate":

                weak = weak_products.sample(
                    n=1
                ).iloc[0]

                strong = moderate_products.sample(
                    n=1
                ).iloc[0]

            else:

                weak = moderate_products.sample(
                    n=1
                ).iloc[0]

                strong = strong_products.sample(
                    n=1
                ).iloc[0]

            # =============================================
            # SAME PRODUCT FIX
            # =============================================
            while weak['product_name'] == strong['product_name']:
                strong = product_df.sample(
                    n=1
                ).iloc[0]

            # =============================================
            # SMART DISCOUNT
            # low selling → more discount
            # =============================================
            weak_sales_score = (
                                       weak['sales'] /
                                       product_df['sales'].max()
                               ) * 100

            if weak_sales_score < 20:

                best_discount = random.randint(
                    25,
                    40
                )

            elif weak_sales_score < 40:

                best_discount = random.randint(
                    15,
                    30
                )

            else:

                best_discount = random.randint(
                    10,
                    20
                )

            # =============================================
            # MODEL
            # =============================================
            (
                ai_score,
                ai_growth,
                original_price,
                combo_price,
                future_revenue,
                estimated_profit
            ) = calculate_combo_metrics(
                weak,
                strong,
                best_discount
            )

            # =============================================
            # STORE RESULT
            # =============================================
            st.session_state.ai_combo_result = {

                "Product A":
                    weak['product_name'],

                "Product B":
                    strong['product_name'],

                "Discount":
                    best_discount,

                "Success":
                    ai_score,

                "Growth":
                    ai_growth,

                "Original":
                    original_price,

                "Combo":
                    combo_price,

                "Revenue":
                    future_revenue,

                "Profit":
                    estimated_profit
            }

        # =================================================
        # SHOW AI COMBO
        # =================================================
        if st.session_state.ai_combo_result:

            result = st.session_state.ai_combo_result

            st.success(f"""
            🎁 AI Suggested Combo

            Product A:
            {result['Product A']}

            Product B:
            {result['Product B']}
            """)

            c1, c2, c3, c4 = st.columns(4)

            c1.metric(
                "Suggested Discount",
                f"{result['Discount']}%"
            )

            c2.metric(
                "Success Rate",
                f"{result['Success']}%"
            )

            c3.metric(
                "Expected Growth",
                f"{result['Growth']}%"
            )

            c4.metric(
                "Predicted Revenue",
                f"{result['Revenue']}"
            )

            st.markdown("---")

            p1, p2 = st.columns(2)

            p1.metric(
                "Original Price",
                f"{result['Original']}"
            )

            p2.metric(
                "Estimated Profit",
                f"{result['Profit']}"
            )

            if st.button(
                "💾 Save AI Combo"
            ):

                st.session_state.ai_history.append({

                    "Type":
                        "AI Combo",

                    **result
                })

                st.success("""
                ✅ AI Combo saved
                """)

        st.markdown("---")

        # =================================================
        # =================================================
        # AI DISCOUNT
        # =================================================
        if st.button(
                "🎲 Generate AI Discount",
                key="generate_ai_discount_btn"
        ):

            # =============================================
            # LOW + MODERATE PRODUCTS
            # =============================================
            target_products = product_df[
                product_df['status'].isin([
                    "⚠️ Weak Demand",
                    "📈 Moderate"
                ])
            ]

            product = target_products.sample(
                n=1
            ).iloc[0]

            # =============================================
            # PRODUCT SCORE
            # =============================================
            sales_score = (
                                  product['sales'] /
                                  product_df['sales'].max()
                          ) * 100

            best_discount = 0
            best_revenue = 0
            best_growth = 0
            best_profit = 0
            best_success = 0

            # =============================================
            # TEST MULTIPLE DISCOUNTS
            # =============================================
            # =============================================
            # =============================================
            # TEST MULTIPLE DISCOUNTS
            # =============================================

            for discount in random.sample(range(5, 51), 12):

                # =========================================
                # LOW SELLING BOOST
                # =========================================
                low_sales_factor = (
                        (
                                100 - sales_score
                        ) * 0.25
                )

                # =========================================
                # DISCOUNT EFFICIENCY
                # =========================================
                if discount <= 10:

                    discount_efficiency = (
                            discount * 1.9
                    )

                elif discount <= 20:

                    discount_efficiency = (
                            discount * 1.5
                    )

                elif discount <= 30:

                    discount_efficiency = (
                            discount * 1.0
                    )

                elif discount <= 40:

                    discount_efficiency = (
                            discount * 0.5
                    )

                else:

                    discount_efficiency = (
                            discount * 0.2
                    )

                # =========================================
                # RANDOM MARKET VARIATION
                # =========================================
                market_variation = random.uniform(
                    -4,
                    7
                )

                # =========================================
                # DEMAND GROWTH
                # =========================================
                demand_growth = (
                        low_sales_factor +
                        discount_efficiency +
                        market_variation
                )

                demand_growth = max(
                    5,
                    min(70, demand_growth)
                )

                # =========================================
                # FUTURE REVENUE
                # =========================================
                future_revenue = (
                        product['revenue'] *
                        (
                                1 +
                                demand_growth / 100
                        )
                )

                # =========================================
                # PROFIT MARGIN
                # =========================================
                profit_margin = (
                        (
                                1 -
                                discount / 100
                        ) * 0.28
                )

                estimated_profit = (
                        future_revenue *
                        profit_margin
                )

                # =========================================
                # SMART SUCCESS SCORE
                # =========================================
                success = (
                        demand_growth * 0.8
                        +
                        (100 - sales_score) * 0.5
                        -
                        discount * 0.4
                )

                # =========================================
                # HIGH DISCOUNT PENALTY
                # =========================================
                if discount > 35:
                    success -= 10

                if estimated_profit < 0:
                    success -= 30

                # =========================================
                # BEST RESULT
                # =========================================
                # =========================================
                # DYNAMIC FINAL SCORE
                # =========================================

                final_score = (
                        success
                        +
                        random.uniform(-12, 12)
                )

                # profit priority
                if estimated_profit > 0:
                    final_score += 8

                # extra high discount penalty
                if discount >= 40:
                    final_score -= 15

                # low discount penalty
                if discount <= 5:
                    final_score -= 5

                # =========================================
                # BEST RESULT
                # =========================================
                if final_score > best_success:
                    best_success = final_score

                    best_discount = discount

                    best_growth = demand_growth

                    best_revenue = future_revenue

                    best_profit = estimated_profit
            # =============================================
            # FINAL OUTPUT
            # =============================================
            st.session_state.ai_discount_result = {

                "Product":
                    product['product_name'],

                "Discount":
                    round(best_discount, 0),

                "Growth":
                    round(best_growth, 1),

                "Revenue":
                    round(best_revenue, 0),

                "Profit":
                    round(best_profit, 0),

                "Success":
                    round(best_success, 1)
            }


        # =================================================
        # =================================================
        # SHOW AI DISCOUNT
        # =================================================
        if st.session_state.ai_discount_result:

            discount_result = st.session_state.ai_discount_result

            st.info(f"""
            💸 AI Discount Suggestion

            Product:
            {discount_result['Product']}
            """)

            # =========================================
            # METRICS
            # =========================================
            d1, d2, d3, d4, d5 = st.columns(5)

            d1.metric(
                "Discount",
                f"{discount_result['Discount']}%"
            )

            d2.metric(
                "Growth",
                f"{discount_result['Growth']}%"
            )

            d3.metric(
                "Revenue",
                f"{discount_result['Revenue']}"
            )

            d4.metric(
                "Profit",
                f"{discount_result['Profit']:.0f}"
            )

            d5.metric(
                "Success",
                f"{discount_result['Success']:.1f}%"
            )

            st.markdown("---")

            # =========================================
            # AI INSIGHT
            # =========================================
            if discount_result['Profit'] <= 0:

                st.error("""
                ❌ Profit Risk Detected
                """)

            elif discount_result['Discount'] > 35:

                st.warning("""
                ⚠️ High Discount Strategy

                Sales may increase
                but margin becomes lower
                """)

            else:

                st.success("""
                🚀 Optimized AI Discount Strategy
                """)

            # =========================================
            # SAVE
            # =========================================
            if st.button(
                    "💾 Save AI Discount"
            ):
                st.session_state.ai_history.append({

                    "Type":
                        "AI Discount",

                    **discount_result
                })

                st.success("""
                ✅ AI Discount saved
                """)

    # =====================================================
    # HISTORY
    # =====================================================
    st.markdown("---")

    st.subheader("🕘 Strategy History")

    all_history = (
        st.session_state.combo_history
        +
        st.session_state.discount_history
        +
        st.session_state.ai_history
    )

    if len(all_history) > 0:

        history_df = pd.DataFrame(
            all_history
        )

        st.dataframe(
            history_df,
            use_container_width=True
        )

    else:

        st.info("""
        No strategy history yet
        """)