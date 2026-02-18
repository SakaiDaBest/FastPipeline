import pandas as pd
import datetime as dt

def cleanCustomers(df):
    if 'name' in df.columns:
        df['name'] = df['name'].str.strip().str.title()

    if 'country' in df.columns:
        df['country'] = df['country'].str.strip().str.title()

    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = df[col].fillna('Unknown')
        else:
            df[col] = df[col].fillna(0)

    if 'email' in df.columns:
        df['email'] = df['email'].str.lower()
    
    if 'signup_date' in df.columns:
        df['signup_date'] = pd.to_datetime(df['signup_date'],format='mixed', errors='coerce', dayfirst=False)
        df['signup_date'] = df['signup_date'].dt.strftime('%Y-%m-%d')
    
    return df

