import os
import pandas as pd
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from tensorflow.keras import metrics
from sklearn.preprocessing import MinMaxScaler
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env

# Database connection
DBNAME = os.getenv('dbname')
POSTGRES_USER = os.getenv('postgres_user')
POSTGRES_PASSWORD = os.getenv('postgres_password')
POSTGRES_HOST = os.getenv('postgres_host')
DATABASE_URI = f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}/{DBNAME}'
engine = create_engine(DATABASE_URI)

# Fetch historical data
def get_historical_data(coin_id):
    query = f"SELECT timestamp, close FROM crypto_data WHERE coin_id = '{coin_id}' ORDER BY timestamp ASC"
    return pd.read_sql(query, engine)

# Prepare data
def prepare_data(data, look_back=30):
    scaler = MinMaxScaler()
    scaled_data = scaler.fit_transform(data.values.reshape(-1, 1))
    X, y = [], []
    for i in range(len(scaled_data) - look_back):
        X.append(scaled_data[i:i + look_back])
        y.append(scaled_data[i + look_back])
    return np.array(X), np.array(y), scaler

# Train LSTM model
def train_lstm_model(X_train, y_train, look_back):
    model = Sequential([
        LSTM(50, return_sequences=True, input_shape=(look_back, 1)),
        LSTM(50),
        Dense(1)
    ])
    # Compile the model with 'mse' explicitly defined
    model.compile(optimizer='adam', loss='mse', metrics=[metrics.MeanSquaredError()])
    model.fit(X_train, y_train, epochs=20, batch_size=32, validation_split=0.2)
    return model

# Save the model
def save_model(model, file_path='lstm_model.h5'):
    model.save(file_path)
    print(f"Model saved to {file_path}")

# Main process
if __name__ == "__main__":
    coin_id = 'BTC'  # Replace with desired coin ID
    data = get_historical_data(coin_id)
    X, y, scaler = prepare_data(data['close'])
    model = train_lstm_model(X, y, look_back=30)
    save_model(model, 'lstm_model.h5')
