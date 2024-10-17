from django.core.management.base import BaseCommand
import requests
import csv
from decouple import config
from fetchfinancialdata.models import StockData

class Command(BaseCommand):
    help = 'Fetch stock data from Alpha Vantage API and save it to CSV'

    def handle(self, *args, **kwargs):
        API_KEY = config('ALPHA_VANTAGE_API_KEY')
        symbol = 'AAPL'
        url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={API_KEY}'

        response = requests.get(url)
        data = response.json()

        # Check if the response contains the expected data
        if 'Time Series (Daily)' not in data:
            self.stdout.write(self.style.ERROR('Failed to fetch stock data'))
            return

        time_series = data['Time Series (Daily)']

        # Save the data to a CSV file
        with open('stock_data.csv', mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Date', 'Open', 'High', 'Low', 'Close', 'Volume'])

            for date_str, daily_data in time_series.items():
                date = date_str
                open_price = daily_data['1. open']
                high_price = daily_data['2. high']
                low_price = daily_data['3. low']
                close_price = daily_data['4. close']
                volume = daily_data['5. volume']

                # Save to the database
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

                # Write to CSV
                writer.writerow([date, open_price, high_price, low_price, close_price, volume])

        self.stdout.write(self.style.SUCCESS('Stock data fetched and saved successfully!'))
