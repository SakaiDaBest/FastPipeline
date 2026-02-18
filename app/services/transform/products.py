import pandas as pd

def cleanProducts(df):
    if 'total_amount' in df.columns:
        df['total_amount'] = df['total_amount'].str.extract(r'(\d+\.?\d*)').astype(float)
    if 'category' in df.columns:
        df['category'] = df['category'].str.title()

    return df
