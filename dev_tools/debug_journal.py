from dashboard_server import JOURNAL_PATH
import pandas as pd
import os

print(f"Reading {JOURNAL_PATH}...")
column_names = ['timestamp', 'order_id', 'symbol', 'action', 'price', 'quantity', 'taxes', 'total_cost']
df = pd.read_csv(JOURNAL_PATH, names=column_names, on_bad_lines='skip')
print(f"Raw Rows: {len(df)}")
print("First 5 rows:")
print(df.head())

print("\n--- Parsed Timestamps ---")
df['dt_temp'] = pd.to_datetime(df['timestamp'], errors='coerce')
print(df[['timestamp', 'dt_temp']].head())
print(f"Rows after dropna matches: {len(df.dropna(subset=['dt_temp']))}")

print("\n--- Testing Logic Loop ---")
from dashboard_server import get_alpha_details
data = get_alpha_details()
print(f"Final Output count: {len(data)}")
if len(data) > 0:
    print(data[0])
