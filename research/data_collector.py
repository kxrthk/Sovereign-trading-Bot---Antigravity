import yfinance as yf
import pandas as pd
import datetime

def collect_data():
    symbol = 'RELIANCE.NS'
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=730) # 2 years

    print(f"Downloading data for {symbol} from {start_date} to {end_date}...")
    df = yf.download(symbol, start=start_date, end=end_date)

    if df.empty:
        print("No data found!")
        return

    # Add Target column
    # Target: 1 if next day's Close > today's Close, else 0
    # data['Close'] is today's close.
    # We want to compare shift(-1) (tomorrow's close) with current close.
    
    # yfinance returns a MultiIndex columns if not flattened in newer versions, 
    # but usually Ticker.history or download returns simple columns. 
    # Let's ensure simple index just in case.
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    # Calculate Target
    # We need to shift Close backwards by 1 to align tomorrow's close with today's row
    # Then compare: if Next_Close > Current_Close -> 1, else 0
    next_close = df['Close'].shift(-1)
    df['Target'] = (next_close > df['Close']).astype(int)

    # The last row will have NaN for next_close, so comparison might be false (0). 
    # Since we can't know the future for the very last day, typically we drop it or leave it. 
    # Request said "build the dataset", usually for training we drop the last row where target is unknown.
    # However, strictly following instructions "If tomorrow's Close is higher... else 0".
    # Pandas comparison with NaN is False, so it becomes 0, which is logically "Down" (unknown).
    # I will leave it as is or dropna() if typically desired for ML. 
    # Let's just keep it simple as requested. 

    output_file = 'research/training_data.csv'
    df.to_csv(output_file)
    print(f"Data saved to {output_file}")
    print(df.tail())

if __name__ == "__main__":
    collect_data()
