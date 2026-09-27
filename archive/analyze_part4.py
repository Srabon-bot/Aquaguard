import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings("ignore")

df = pd.read_csv(r"D:/Projects/pred_flood/archive/65 Years of Weather Data Bangladesh (1948 - 2013).csv")
df.columns = df.columns.str.strip()

# 4. Data completeness
print("=" * 80)
print("4. DATA COMPLETENESS PER COLUMN")
print("=" * 80)
header = f"{'Column':<25s} {'Non-Null':>10s} {'Missing':>10s} {'% Missing':>10s} {'% Complete':>10s}"
print(header)
print("-" * 75)
for col in df.columns:
    non_null = df[col].notna().sum()
    missing = df[col].isna().sum()
    pct_miss = (missing / len(df)) * 100
    pct_comp = (non_null / len(df)) * 100
    print(f"{col:<25s} {non_null:>10,d} {missing:>10,d} {pct_miss:>9.2f}% {pct_comp:>9.2f}%")

print()
print("Potential placeholder/empty string values:")
for col in df.columns:
    if df[col].dtype == object:
        empty_str = (df[col] == "").sum()
        if empty_str > 0:
            print(f"  {col}: {empty_str} empty strings")
