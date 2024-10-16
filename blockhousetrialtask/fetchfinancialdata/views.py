from django.shortcuts import render
import requests
from decouple import config
from .models import StockData

def fetch_stock_data(request):
    API_KEY = config('ALPHA_VANTAGE_API_KEY')
    symbol = 'AAPL'
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={API_KEY}'

    response = requests.get(url)
    data = response.json()

    if 'Time Series (Daily)' not in data:
        return render(request, 'error.html', {'error': 'Failed to fetch data'})

    time_series = data['Time Series (Daily)']
    for date_str, daily_data in time_series.items():
        date = date_str
        open_price = daily_data['1. open']
        high_price = daily_data['2. high']
        low_price = daily_data['3. low']
        close_price = daily_data['4. close']
        volume = daily_data['5. volume']

        StockData.objects.update_or_create(
            symbol=symbol,
            date=date,
            defaults={
                'open_price': open_price,
                'high_price': high_price,
                'low_price': low_price,
                'close_price': close_price,
                'volume': volume,
            }
        )

    return render(request, 'success.html', {'message': 'Stock data fetched and saved successfully!'})
