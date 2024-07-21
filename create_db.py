import sqlite3
from sqlite3 import Error

def create_connection(db_file):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(sqlite3.version)
    except Error as e:
        print(e)
    return conn

def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)

def main():
    database = r"ngocvu_data.db"  # Path to the SQLite database file

    sql_create_orders_table = """ CREATE TABLE IF NOT EXISTS Orders (
                                        order_id INTEGER PRIMARY KEY AUTOINCREMENT,
                                        date TEXT NOT NULL,
                                        customer_code TEXT,
                                        street_name TEXT,
                                        product_type TEXT,
                                        bottle_type TEXT,
                                        quantity_delivered INTEGER,
                                        bottle_returned INTEGER,
                                        amount_paid REAL,
                                        payment_method TEXT
                                    ); """

    sql_create_customers_table = """ CREATE TABLE IF NOT EXISTS Customers (
                                        customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
                                        customer_name TEXT NOT NULL,
                                        A350 REAL,
                                        A500 REAL,
                                        A1_5 REAL,
                                        A5_0 REAL,
                                        O350 REAL,
                                        O600 REAL,
                                        O1_5 REAL,
                                        NV REAL,
                                        PN REAL,
                                        TB REAL,
                                        P350 REAL,
                                        P500 REAL,
                                        T350 REAL,
                                        ION REAL
                                    ); """

    sql_create_streets_table = """ CREATE TABLE IF NOT EXISTS Streets (
                                        street_code TEXT PRIMARY KEY,
                                        street_name TEXT NOT NULL
                                    ); """

    # create a database connection
    conn = create_connection(database)

    # create tables
    if conn is not None:
        # create orders table
        create_table(conn, sql_create_orders_table)
        # create customers table
        create_table(conn, sql_create_customers_table)
        # create streets table
        create_table(conn, sql_create_streets_table)
        conn.close()
    else:
        print("Error! cannot create the database connection.")

if __name__ == '__main__':
    main()
