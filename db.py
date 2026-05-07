import psycopg2

def get_conn():
    return psycopg2.connect(
        dbname="business analysis",
        user="postgres",
        password="noyon66966",
        host="localhost",
        port="5432"
    )