import pandas as pd
import psycopg2

def load_data():
    conn = psycopg2.connect(
        dbname="business analysis",
        user="postgres",
        password="noyon66966",
        host="localhost",
        port="5432"
    )

    customers = pd.read_sql("SELECT * FROM customers", conn)
    products = pd.read_sql("SELECT * FROM products", conn)
    orders = pd.read_sql("SELECT * FROM orders", conn)
    sales = pd.read_sql("SELECT * FROM sales", conn)

    df = sales.merge(orders, on='order_id') \
              .merge(customers, on='customer_id') \
              .merge(products, on='product_id')

    df['order_date'] = pd.to_datetime(df['order_date'])

    return df