CREATE TABLE IF NOT EXISTS crypto_data (
        id SERIAL PRIMARY KEY,
        coin_id VARCHAR(50),
        timestamp TIMESTAMP,
        open NUMERIC,
        high NUMERIC,
        low NUMERIC,
        close NUMERIC
    );