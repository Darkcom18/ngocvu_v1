import sqlite3
import pandas as pd
import streamlit as st
from sqlalchemy import create_engine
from datetime import datetime

# Create SQLite database connection
def create_db_connection():
    return sqlite3.connect('delivery_data.db')

# Initialize database
def init_db():
    conn = create_db_connection()
    cursor = conn.cursor()

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
            product_id INTEGER,
            price REAL,
            last_updated TIMESTAMP,
            FOREIGN KEY (customer_id) REFERENCES customers (customer_id),
            FOREIGN KEY (product_id) REFERENCES products (product_id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventory (
            inventory_id INTEGER PRIMARY KEY,
            product_id INTEGER,
            quantity INTEGER,
            last_updated TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products (product_id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sales (
            sale_id INTEGER PRIMARY KEY,
            product_id INTEGER,
            quantity INTEGER,
            sale_date DATE,
            FOREIGN KEY (product_id) REFERENCES products (product_id)
        )
    ''')

    conn.commit()
    conn.close()

# Populate customers table
def populate_customers(unique_customers):
    conn = create_db_connection()
    cursor = conn.cursor()

    for customer in unique_customers:
        cursor.execute('INSERT OR IGNORE INTO customers (customer_name) VALUES (?)', (customer,))

    conn.commit()
    conn.close()

# Insert or update product
def insert_or_update_product(product_name):
    conn = create_db_connection()
    cursor = conn.cursor()

    cursor.execute('INSERT OR IGNORE INTO products (product_name) VALUES (?)', (product_name,))
    conn.commit()
    conn.close()

# Insert sales data from provided dataframes
def insert_sales_data(data):
    conn = create_db_connection()
    cursor = conn.cursor()

    product_names = cursor.execute('SELECT product_name FROM products').fetchall()
    product_names = [p[0] for p in product_names]

    for _, row in data.iterrows():
        product_name = row['Loại sản phẩm']
        if product_name in product_names:
            product_id = cursor.execute('SELECT product_id FROM products WHERE product_name = ?', (product_name,)).fetchone()[0]
            cursor.execute('''
                INSERT INTO sales (product_id, quantity, sale_date)
                VALUES (?, ?, ?)
            ''', (product_id, row['Số lượng Giao'], row['Ngày']))
    
    conn.commit()
    conn.close()

def get_products():
    conn = create_db_connection()
    product_df = pd.read_sql_query("SELECT * FROM products", conn)
    conn.close()
    return product_df

def get_inventory():
    conn = create_db_connection()
    inventory_df = pd.read_sql_query('''
        SELECT p.product_name, i.quantity, i.last_updated
        FROM inventory i
        JOIN products p ON i.product_id = p.product_id
    ''', conn)
    conn.close()
    return inventory_df

def update_inventory(product_id, inventory_quantity):
    conn = create_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO inventory (product_id, quantity, last_updated)
        VALUES (?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(product_id) DO UPDATE SET
        quantity = excluded.quantity,
        last_updated = excluded.last_updated
    ''', (product_id, inventory_quantity))
    conn.commit()
    conn.close()

def calculate_remaining_inventory(product_id):
    conn = create_db_connection()
    cursor = conn.cursor()

    # Calculate total sales for the product
    sales_df = pd.read_sql_query('''
        SELECT SUM(quantity) as total_sales
        FROM sales
        WHERE product_id = ?
    ''', conn, params=(product_id,))
    
    # Check if the DataFrame is empty
    if sales_df.empty or sales_df['total_sales'].isnull().values[0]:
        total_sales = 0
    else:
        total_sales = sales_df['total_sales'].values[0]

    # Get current inventory for the product
    current_inventory_df = pd.read_sql_query('''
        SELECT quantity
        FROM inventory
        WHERE product_id = ?
    ''', conn, params=(product_id,))
    
    # Check if the DataFrame is empty
    if current_inventory_df.empty or current_inventory_df['quantity'].isnull().values[0]:
        current_inventory = 0
    else:
        current_inventory = current_inventory_df['quantity'].values[0]

    # Calculate remaining inventory
    remaining_inventory = current_inventory - total_sales
    conn.close()
    return remaining_inventory


def generate_summary(data):
    data['Ngày'] = pd.to_datetime(data['Ngày'])
    daily_summary = data.groupby(['Ngày', 'Loại sản phẩm'])[['Số lượng Giao', 'Vỏ về']].sum().reset_index()
    return daily_summary

def run_inventory_management_app(data_xe_may, data_oto):
    init_db()

    # Populate customer and product tables
    unique_customers_xe_may = data_xe_may['Khách hàng ( Hoặc số địa chỉ)'].unique()
    unique_customers_oto = data_oto['Khách hàng ( Hoặc số địa chỉ)'].unique()
    populate_customers(unique_customers_xe_may)
    populate_customers(unique_customers_oto)

    conn = create_db_connection()
    cursor = conn.cursor()

    # Add product
    st.subheader("Add Product")
    product_name = st.text_input("Product Name")
    if st.button("Add Product"):
        insert_or_update_product(product_name)
        st.success(f"Product '{product_name}' added successfully")

    # Display products
    st.subheader("Products")
    product_df = get_products()
    st.write(product_df)

    # Add sales data
    st.subheader("Insert Sales Data from CSV")
    if st.button("Insert Sales Data for Xe May"):
        insert_sales_data(data_xe_may)
        st.success("Sales data for Xe May inserted successfully")
    if st.button("Insert Sales Data for Oto"):
        insert_sales_data(data_oto)
        st.success("Sales data for Oto inserted successfully")

    # Manage Inventory
    st.subheader("Manage Inventory")
    selected_product = st.selectbox("Select Product", product_df['product_name'])
    inventory_quantity = st.number_input("Enter Quantity", min_value=0)

    if st.button("Update Inventory"):
        product_id_row = product_df[product_df['product_name'] == selected_product]
        if not product_id_row.empty:
            product_id = product_id_row['product_id'].values[0]
            update_inventory(product_id, inventory_quantity)
            st.success(f"Inventory for '{selected_product}' updated successfully")
        else:
            st.error(f"Product '{selected_product}' not found")

    # Display inventory
    st.subheader("Inventory")
    inventory_df = get_inventory()
    st.write(inventory_df)

    # Calculate remaining inventory
    st.subheader("Calculate Remaining Inventory")
    selected_product = st.selectbox("Select Product to Calculate Remaining Inventory", product_df['product_name'])
    product_id_row = product_df[product_df['product_name'] == selected_product]
    if not product_id_row.empty:
        product_id = product_id_row['product_id'].values[0]
        remaining_inventory = calculate_remaining_inventory(product_id)
        st.write(f"Remaining inventory for '{selected_product}': {remaining_inventory}")
    else:
        st.error(f"Product '{selected_product}' not found")

    # Debt Management
    st.subheader("Debt Management - Xe May")
    daily_summary_xe_may = generate_summary(data_xe_may)
    period = st.selectbox("Select Period", ["Day", "Week", "Month", "Year"])

    if period == "Day":
        daily_summary_xe_may_filtered = daily_summary_xe_may
    elif period == "Week":
        # Group by week and product
        daily_summary_xe_may.set_index('Ngày', inplace=True)
        daily_summary_xe_may_filtered = daily_summary_xe_may.groupby([pd.Grouper(freq='W'), 'Loại sản phẩm']).sum().reset_index()
    elif period == "Month":
        # Group by month and product
        daily_summary_xe_may.set_index('Ngày', inplace=True)
        daily_summary_xe_may_filtered = daily_summary_xe_may.groupby([pd.Grouper(freq='M'), 'Loại sản phẩm']).sum().reset_index()
    elif period == "Year":
        # Group by year and product
        daily_summary_xe_may.set_index('Ngày', inplace=True)
        daily_summary_xe_may_filtered = daily_summary_xe_may.groupby([pd.Grouper(freq='Y'), 'Loại sản phẩm']).sum().reset_index()

    st.write(daily_summary_xe_may_filtered)

    st.subheader("Debt Management - Oto")
    daily_summary_oto = generate_summary(data_oto)

    if period == "Day":
        daily_summary_oto_filtered = daily_summary_oto
    elif period == "Week":
        # Group by week and product
        daily_summary_oto.set_index('Ngày', inplace=True)
        daily_summary_oto_filtered = daily_summary_oto.groupby([pd.Grouper(freq='W'), 'Loại sản phẩm']).sum().reset_index()
    elif period == "Month":
        # Group by month and product
        daily_summary_oto.set_index('Ngày', inplace=True)
        daily_summary_oto_filtered = daily_summary_oto.groupby([pd.Grouper(freq='M'), 'Loại sản phẩm']).sum().reset_index()
    elif period == "Year":
        # Group by year and product
        daily_summary_oto.set_index('Ngày', inplace=True)
        daily_summary_oto_filtered = daily_summary_oto.groupby([pd.Grouper(freq='Y'), 'Loại sản phẩm']).sum().reset_index()

    st.write(daily_summary_oto_filtered)

    conn.close()
