import sqlite3
import pandas as pd
conn = sqlite3.connect('customer_pricing.db')
query = 'SELECT * FROM prices'
df = pd.read_sql_query(query, conn)
print(df)
conn.close()
