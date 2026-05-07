import streamlit as st
import pandas as pd
from db import get_conn

def admin_panel(df):

    # ================= CSS =================
    st.markdown("""
    <style>
    div[data-baseweb="input"] > div {
        border-radius: 10px;
    }

    .valid-box div[data-baseweb="input"] > div {
        border: 2px solid #00b894 !important;
        background-color: #f0fff5 !important;
    }

    .invalid-box div[data-baseweb="input"] > div {
        border: 2px solid #d63031 !important;
        background-color: #fff5f5 !important;
    }

    .msg-ok {
        color: #00b894;
        font-size: 12px;
        margin-top: -5px;
        margin-bottom: 8px;
    }

    .msg-err {
        color: #d63031;
        font-size: 12px;
        margin-top: -5px;
        margin-bottom: 8px;
    }
    </style>
    """, unsafe_allow_html=True)

    st.sidebar.title("⚙️ Admin Panel")

    # ================= CSV =================
    file = st.sidebar.file_uploader("📤 Upload CSV")

    if file:
        new = pd.read_csv(file)
        st.write(new.head())

        if st.sidebar.button("Insert CSV"):
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

    # ================= FORM =================
    st.sidebar.title("👤 Add Customer")

    cid = st.sidebar.number_input("Customer ID", min_value=1)

    # -------- NAME --------
    name = st.sidebar.text_input("Customer Name")
    if name != "":
        if name.replace(" ", "").isalpha():
            st.sidebar.markdown('<div class="valid-box"></div>', unsafe_allow_html=True)
            st.sidebar.markdown('<div class="msg-ok">✔ Valid name</div>', unsafe_allow_html=True)
        else:
            st.sidebar.markdown('<div class="invalid-box"></div>', unsafe_allow_html=True)
            st.sidebar.markdown('<div class="msg-err">❌ Only letters allowed</div>', unsafe_allow_html=True)

    # -------- GENDER --------
    gender = st.sidebar.selectbox("Gender", ["Male", "Female", "Other"])

    # -------- AGE --------
    age = st.sidebar.number_input("Age", min_value=1, max_value=120)
    if age != 0:
        if 0 < age <= 120:
            st.sidebar.markdown('<div class="msg-ok">✔ Valid age</div>', unsafe_allow_html=True)
        else:
            st.sidebar.markdown('<div class="msg-err">❌ Age must be 1-120</div>', unsafe_allow_html=True)

    # -------- ADDRESS --------
    address = st.sidebar.text_area("Address")
    if address != "":
        if len(address.strip()) >= 5:
            st.sidebar.markdown('<div class="msg-ok">✔ Address OK</div>', unsafe_allow_html=True)
        else:
            st.sidebar.markdown('<div class="msg-err">❌ Too short</div>', unsafe_allow_html=True)

    # -------- ZIP --------
    zip_code = st.sidebar.text_input("Zip Code")
    if zip_code != "":
        if zip_code.isdigit():
            st.sidebar.markdown('<div class="msg-ok">✔ Valid zip</div>', unsafe_allow_html=True)
        else:
            st.sidebar.markdown('<div class="msg-err">❌ Numbers only</div>', unsafe_allow_html=True)

    # -------- CITY --------
    city = st.sidebar.text_input("City")
    if city != "":
        if len(city.strip()) >= 2:
            st.sidebar.markdown('<div class="msg-ok">✔ City OK</div>', unsafe_allow_html=True)
        else:
            st.sidebar.markdown('<div class="msg-err">❌ Invalid city</div>', unsafe_allow_html=True)

    # -------- STATE --------
    state = st.sidebar.text_input("State")
    if state != "":
        if len(state.strip()) >= 2:
            st.sidebar.markdown('<div class="msg-ok">✔ State OK</div>', unsafe_allow_html=True)
        else:
            st.sidebar.markdown('<div class="msg-err">❌ Invalid state</div>', unsafe_allow_html=True)

    # -------- COUNTRY --------
    country = st.sidebar.text_input("Country")
    if country != "":
        if len(country.strip()) >= 2:
            st.sidebar.markdown('<div class="msg-ok">✔ Country OK</div>', unsafe_allow_html=True)
        else:
            st.sidebar.markdown('<div class="msg-err">❌ Invalid country</div>', unsafe_allow_html=True)

    # ================= SUBMIT =================
    if st.sidebar.button("Add Customer"):

        errors = []

        if name.strip() == "":
            errors.append("Name required")

        if not name.replace(" ", "").isalpha():
            errors.append("Invalid name")

        if not zip_code.isdigit():
            errors.append("Zip must be numeric")

        if address.strip() == "":
            errors.append("Address required")

        if city.strip() == "":
            errors.append("City required")

        if state.strip() == "":
            errors.append("State required")

        if country.strip() == "":
            errors.append("Country required")

        if len(errors) > 0:
            st.error("❌ Fix errors:")
            for e in errors:
                st.write("-", e)

        else:
            conn = get_conn()
            cur = conn.cursor()

            cur.execute("SELECT * FROM customers WHERE customer_id = %s", (cid,))
            if cur.fetchone():
                st.error("Customer already exists")

            else:
                cur.execute("""
                INSERT INTO customers (
                    customer_id, customer_name, gender, age,
                    home_address, zip_code, city, state, country
                )
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """, (
                    int(cid), name, gender, int(age),
                    address, zip_code, city, state, country
                ))

                conn.commit()
                conn.close()

                st.success("✅ Customer Added Successfully")
                st.rerun()