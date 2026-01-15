import akshare as ak
df = ak.stock_zh_a_hist(symbol="000001", period="daily", start_date="20240101", end_date="20250101", adjust="qfq")
print("Columns:", df.columns.tolist())
print("Head:\n", df.head())
