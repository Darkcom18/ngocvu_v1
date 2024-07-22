import pandas as pd
import sqlite3
from datetime import datetime
import streamlit as st

# Database Setup
def create_and_init_db():
    conn = sqlite3.connect('customer_pricing.db')
    cursor = conn.cursor()

    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            customer_id INTEGER PRIMARY KEY,
            customer_name TEXT NOT NULL UNIQUE
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            product_id INTEGER PRIMARY KEY,
            product_name TEXT NOT NULL UNIQUE
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS prices (
            price_id INTEGER PRIMARY KEY,
            customer_id INTEGER,
            product_name TEXT,
            price REAL,
            last_updated TIMESTAMP,
            FOREIGN KEY (customer_id) REFERENCES customers (customer_id),
            UNIQUE (customer_id, product_name)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventory (
            product_id INTEGER PRIMARY KEY,
            quantity INTEGER,
            FOREIGN KEY (product_id) REFERENCES products (product_id)
        )
    ''')

    conn.commit()
    conn.close()

# Initialize the database
create_and_init_db()

# Database Connection
def create_db_connection(db_name='customer_pricing.db'):
    try:
        conn = sqlite3.connect(db_name)
        print("Database connection successful")
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")

def get_customers():
    conn = create_db_connection()
    df = pd.read_sql_query('SELECT * FROM customers', conn)
    conn.close()
    return df

def get_products():
    conn = create_db_connection('delivery_data.db')
    df = pd.read_sql_query('SELECT * FROM products', conn)
    conn.close()
    return df

def get_prices():
    conn = create_db_connection()
    prices_df = pd.read_sql_query('''
        SELECT pr.product_name, c.customer_name, pr.price, pr.last_updated
        FROM prices pr
        JOIN customers c ON pr.customer_id = c.customer_id
    ''', conn)
    conn.close()
    return prices_df

def insert_or_update_price(customer_name, product_name, price):
    conn = create_db_connection()
    cursor = conn.cursor()

    # Check if customer exists
    customer_id = cursor.execute('SELECT customer_id FROM customers WHERE customer_name = ?', (customer_name,)).fetchone()

    if customer_id:
        customer_id = customer_id[0]

        # Insert or update price
        cursor.execute('''
            INSERT INTO prices (customer_id, product_name, price, last_updated)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(customer_id, product_name) DO UPDATE SET
            price = excluded.price,
            last_updated = excluded.last_updated
        ''', (customer_id, product_name, price, datetime.now()))

        conn.commit()
        st.success(f"Price updated successfully for customer '{customer_name}' and product '{product_name}'.")
    else:
        st.error(f"Customer not found. Customer ID: {customer_id}")
    
    conn.close()

def load_and_process_data(xe_may_df, oto_df):
    # Check input data types
    if not isinstance(xe_may_df, pd.DataFrame) or not isinstance(oto_df, pd.DataFrame):
        raise ValueError("Input data must be pandas DataFrame.")
    
    # Process data
    if 'Khách hàng ( Hoặc số địa chỉ)' in xe_may_df.columns and 'Tên đường' in xe_may_df.columns:
        xe_may_df['Khách hàng'] = xe_may_df['Khách hàng ( Hoặc số địa chỉ)'] + ' - ' + xe_may_df['Tên đường']
    else:
        raise KeyError("Required columns are missing in xe_may_df.")

    if 'Khách hàng ( Hoặc số địa chỉ)' in oto_df.columns:
        oto_df['Khách hàng'] = oto_df['Khách hàng ( Hoặc số địa chỉ)']
    else:
        raise KeyError("Required columns are missing in oto_df.")

    # Combine data
    combined_df = pd.concat([xe_may_df[['Khách hàng']], oto_df[['Khách hàng']]])

    # Remove duplicates and save to database
    unique_customers = combined_df['Khách hàng'].unique()

    conn = create_db_connection()
    cursor = conn.cursor()

    for customer in unique_customers:
        cursor.execute('INSERT OR IGNORE INTO customers (customer_name) VALUES (?)', (customer,))
    
    conn.commit()
    conn.close()

def run_pricing_app(xe_may_df, oto_df):
    st.title("Customer Pricing Management")

    # Load products from delivery_data.db
    products_df = get_products()
    print("Products DataFrame:")
    print(products_df)

    # Process data
    load_and_process_data(xe_may_df, oto_df)

    # Load existing data
    customers_df = get_customers()
    print("Customers DataFrame:")
    print(customers_df)

    # Display unique customers
    st.subheader("Unique Customers")
    st.write(customers_df)

    # Add/Update Price
    st.subheader("Add or Update Price")
    selected_customer = st.selectbox("Select Customer", options=customers_df['customer_name'])
    
    if not products_df.empty:
        selected_product = st.selectbox("Select Product", options=products_df['product_name'])
    else:
        st.error("No products available")
        return
    
    new_price = st.number_input("Enter Price", min_value=0.0, format="%.2f")

    if st.button("Update Price"):
        insert_or_update_price(selected_customer, selected_product, new_price)
        st.success(f"Price for customer '{selected_customer}' and product '{selected_product}' updated successfully")

    # Filters
    st.subheader("Filter Prices")
    filter_customer = st.selectbox("Filter by Customer", options=['All'] + customers_df['customer_name'].tolist())
    filter_product = st.selectbox("Filter by Product", options=['All'] + products_df['product_name'].tolist())

    prices_df = get_prices()
    print("Prices DataFrame:")
    print(prices_df)
    
    if filter_customer != 'All':
        prices_df = prices_df[prices_df['customer_name'] == filter_customer]
    if filter_product != 'All':
        prices_df = prices_df[prices_df['product_name'] == filter_product]

    if prices_df.empty:
        st.write("No prices available for the selected filters.")
    else:
        st.write(prices_df)

