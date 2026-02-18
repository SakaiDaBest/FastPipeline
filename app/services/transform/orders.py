import pandas as pd
import datetime as dt

def cleanOrders(df):
    if 'order_date' in df.columns:
        df['order_date'] = pd.to_datetime(df['order_date'],format='mixed', errors='coerce', dayfirst=False)
        df['order_date'] = df['order_date'].dt.strftime('%Y-%m-%d')
    if 'total_amount' in df.columns:
        df['total_amount'] = df['total_amount'].str.extract(r'(\d+\.?\d*)').astype(float)
    df.drop_duplicates(subset=None, keep='first', inplace=False, ignore_index=False)

    return df
