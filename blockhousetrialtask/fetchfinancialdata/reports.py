import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import pandas as pd
from io import BytesIO
from blockhousetrialtask.fetchfinancialdata.models import StockData, PredictedStockData

def generate_report(symbol):
    historical_data = StockData.objects.filter(symbol=symbol).order_by('date')
    predicted_data = PredictedStockData.objects.filter(symbol=symbol).order_by('date')

    historical_df = pd.DataFrame(list(historical_data.values()))
    predicted_df = pd.DataFrame(list(predicted_data.values()))

    historical_df['close_price'] = historical_df['close_price'].astype(float)
    predicted_df['predicted_price'] = predicted_df['predicted_price'].astype(float)

    metrics = {
        'Mean Actual Price': historical_df['close_price'].mean(),
        'Mean Predicted Price': predicted_df['predicted_price'].mean(),
        'Actual Price Standard Deviation': historical_df['close_price'].std(),
        'Predicted Price Standard Deviation': predicted_df['predicted_price'].std(),
    }

    plt.figure(figsize=(10, 6))
    plt.plot(historical_df['date'], historical_df['close_price'], label='Actual Prices', color='blue')
    plt.plot(predicted_df['date'], predicted_df['predicted_price'], label='Predicted Prices', color='orange')
    plt.title(f'Stock Price Prediction for {symbol}')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    plt.grid()
    
    buf = BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)

    return metrics, buf
