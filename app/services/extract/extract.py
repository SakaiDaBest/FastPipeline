import pandas as pd

def read_csv(input_file):
    print(f"Reading data from {input_file}")
    return pd.read_csv(input_file)
