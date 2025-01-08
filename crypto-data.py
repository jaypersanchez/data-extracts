import requests
import pandas as pd
from datetime import datetime
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv
import os

# Load database connection info from .env
load_dotenv()
DBNAME = os.getenv('DBNAME')
POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
POSTGRES_HOST = os.getenv('POSTGRES_HOST')

def create_table():
    create_table_query = """
    CREATE TABLE IF NOT EXISTS crypto_data (
        id SERIAL PRIMARY KEY,
        coin_id VARCHAR(50),
        timestamp TIMESTAMP,
        open NUMERIC,
        high NUMERIC,
        low NUMERIC,
        close NUMERIC
    );
    """
    try:
        conn = psycopg2.connect(
            dbname=DBNAME,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            host=POSTGRES_HOST
        )
        cur = conn.cursor()
        cur.execute(create_table_query)
        conn.commit()
        print("Table created successfully or already exists.")
    except Exception as e:
        print(f"Error creating table: {e}")
    finally:
        cur.close()
        conn.close()

def save_to_db(df, coin_id):
    conn = psycopg2.connect(
        dbname=DBNAME,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        host=POSTGRES_HOST
    )
    cur = conn.cursor()

    for _, row in df.iterrows():
        # Check if the data already exists
        cur.execute("""
            SELECT COUNT(*) FROM crypto_data
            WHERE coin_id = %s AND timestamp = %s
        """, (coin_id, row.timestamp))
        
        if cur.fetchone()[0] == 0:  # If no record exists
            cur.execute("""
                INSERT INTO crypto_data (coin_id, timestamp, open, high, low, close)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (coin_id, row.timestamp, row.open, row.high, row.low, row.close))

    conn.commit()
    cur.close()
    conn.close()


def fetch_market_data(coin_id, vs_currency='usd', days='365'):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/ohlc"
    params = {
        'vs_currency': vs_currency,
        'days': days
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

def process_market_data(data):
    # Data returned as [timestamp, open, high, low, close] for each interval
    df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    return df

def main():
    coins = {
        'bitcoin': 'BTC',
        'ethereum': 'ETH',
        'ripple': 'XRP',
        'solana': 'SOL',
    }

    for coin_id, symbol in coins.items():
        print(f"Fetching data for {symbol} ({coin_id})...")
        data = fetch_market_data(coin_id)
        df = process_market_data(data)
        save_to_db(df, symbol)

if __name__ == "__main__":
    main()
