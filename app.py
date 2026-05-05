import streamlit as st
import pandas as pd
import psycopg2
import plotly.express as px
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from datetime import datetime
from prophet import Prophet

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Supershop Overview", layout="wide")

# ---------------- UI STYLE ----------------
st.markdown("""
<style>
.metric-card {
    background:white;
    padding:15px;
    border-radius:12px;
    box-shadow:0px 3px 10px rgba(0,0,0,0.05);
}
.section {
    background:white;
    padding:20px;
    border-radius:12px;
    margin-bottom:20px;
    box-shadow:0px 3px 10px rgba(0,0,0,0.05);
}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center;'>🛒 Supershop Overview</h1>", unsafe_allow_html=True)

# ---------------- DB ----------------
def get_conn():
    return psycopg2.connect(
        dbname="business analysis",
        user="postgres",
        password="noyon66966",
        host="localhost",
        port="5432"
    )

# ---------------- LOAD DATA ----------------
@st.cache_data(ttl=60)
def load_data():
    conn = get_conn()

    customers = pd.read_sql("SELECT * FROM customers", conn)
    products = pd.read_sql("SELECT * FROM products", conn)
    orders = pd.read_sql("SELECT * FROM orders", conn)
    sales = pd.read_sql("SELECT * FROM sales", conn)

    df = sales.merge(orders, on='order_id', how='left') \
              .merge(customers, on='customer_id', how='left') \
              .merge(products, on='product_id', how='left', suffixes=('', '_drop'))

    df = df[[c for c in df.columns if not c.endswith('_drop')]]

    if 'quantity_y' in df.columns:
        df['quantity'] = df['quantity_y']
    elif 'quantity_x' in df.columns:
        df['quantity'] = df['quantity_x']

    df['order_date'] = pd.to_datetime(df['order_date'])

    return df

df = load_data()

# ---------------- REFRESH ----------------
if st.button("🔄 Refresh Dashboard"):
    st.cache_data.clear()
    st.rerun()

# ---------------- SIDEBAR ----------------
st.sidebar.title("⚙️ Admin Panel")

# CSV Upload
file = st.sidebar.file_uploader("📤 Upload CSV", key="csv")

if file:
    new = pd.read_csv(file)
    st.write(new.head())

    if st.sidebar.button("Insert CSV", key="csv_btn"):
        conn = get_conn()
        cur = conn.cursor()
        for _, r in new.iterrows():
            cur.execute("""
            INSERT INTO sales(order_id, product_id, quantity, total_price)
            VALUES (%s,%s,%s,%s)
            """, (r['order_id'], r['product_id'], r['quantity'], r['total_price']))
        conn.commit()
        conn.close()
        st.success("CSV inserted")

# Add Customer
st.sidebar.markdown("### 👤 Add Customer")

cid = st.sidebar.number_input("Customer ID", key="cust_id")
name = st.sidebar.text_input("Customer Name", key="cust_name")

if st.sidebar.button("Add Customer", key="cust_btn"):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO customers VALUES (%s,%s,CURRENT_DATE)", (cid, name))
    conn.commit()
    conn.close()
    st.success("Customer Added")

# Add Order
st.sidebar.markdown("### 🛒 Add Order")

oid = st.sidebar.number_input("Order ID", key="order_id")
cust = st.sidebar.number_input("Customer ID (Order)", key="order_cust")
date = st.sidebar.date_input("Order Date", key="order_date")

pid = st.sidebar.number_input("Product ID", key="prod_id")
qty = st.sidebar.number_input("Quantity", key="qty")
total = st.sidebar.number_input("Total Price", key="total")

if st.sidebar.button("Add Order", key="order_btn"):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO orders VALUES (%s,%s,%s)", (oid, cust, date))
    cur.execute("INSERT INTO sales VALUES (%s,%s,%s,%s)", (oid, pid, qty, total))
    conn.commit()
    conn.close()
    st.success("Order Added")

# ---------------- FILTER ----------------
start = st.sidebar.date_input("Start Date", df['order_date'].min(), key="start")
end = st.sidebar.date_input("End Date", df['order_date'].max(), key="end")

df = df[(df['order_date'] >= pd.to_datetime(start)) &
        (df['order_date'] <= pd.to_datetime(end))]

# ---------------- KPI ----------------
col1, col2, col3 = st.columns(3)
col1.metric("💰 Revenue", f"{df['total_price'].sum():,.0f}")
col2.metric("📦 Orders", df['order_id'].nunique())
col3.metric("👥 Customers", df['customer_id'].nunique())

# ---------------- TABS ----------------
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["📊 Overview", "📦 Products", "👥 Customers", "🔥 Heatmap", "🔮 Forecast"]
)

# ---------------- OVERVIEW ----------------
with tab1:
    sales = df.groupby('order_date', as_index=False)['total_price'].sum()
    st.plotly_chart(px.line(sales, x='order_date', y='total_price'), use_container_width=True)
    st.info("📌 Sales trend shows business growth")
    st.write("🎯 Action: Improve low performing periods")

# ---------------- PRODUCTS ----------------
with tab2:
    prod = df.groupby('product_name', as_index=False)['quantity'].sum()
    prod = prod.sort_values(by='quantity', ascending=False)

    col1, col2 = st.columns(2)
    col1.plotly_chart(px.bar(prod.head(10), x='product_name', y='quantity'), use_container_width=True)
    col2.plotly_chart(px.pie(prod.head(5), names='product_name', values='quantity'), use_container_width=True)

    st.info("📌 Top products dominate sales")
    st.write("🎯 Action: Increase stock")

# ---------------- CUSTOMERS ----------------
with tab3:
    today = datetime.today()

    rfm = df.groupby('customer_id').agg({
        'order_date': lambda x: (today-x.max()).days,
        'order_id':'count',
        'total_price':'sum'
    })

    scaled = StandardScaler().fit_transform(rfm)
    rfm['cluster'] = KMeans(n_clusters=3).fit_predict(scaled)

    st.plotly_chart(px.scatter(rfm, x='order_id', y='total_price',
                               color=rfm['cluster'].astype(str)))

    st.info("📌 Customer segmentation complete")
    st.write("🎯 Action: Focus on VIP customers")

# ---------------- HEATMAP ----------------
with tab4:
    pivot = df.pivot_table(values='total_price',
                           index='product_name',
                           columns=df['order_date'].dt.month,
                           aggfunc='sum')

    st.plotly_chart(px.imshow(pivot), use_container_width=True)
    st.write("🎯 Action: Prepare for peak months")

# ---------------- FORECAST ----------------
with tab5:
    d = df.groupby('order_date', as_index=False)['quantity'].sum()
    d.columns = ['ds','y']

    model = Prophet()
    model.fit(d)

    future = model.make_future_dataframe(periods=30)
    fc = model.predict(future)

    st.plotly_chart(px.line(fc, x='ds', y='yhat'), use_container_width=True)

    if fc['yhat'].iloc[-1] > fc['yhat'].iloc[0]:
        st.success("Demand increasing")
    else:
        st.warning("Demand decreasing")