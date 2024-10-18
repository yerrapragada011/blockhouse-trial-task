from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.core.management import call_command
from io import StringIO
import requests
from .forms import BacktestForm
from .models import StockData, PredictedStockData
from .reports import generate_report
import pandas as pd
from decimal import Decimal
import numpy as np
import joblib
from datetime import timedelta
from django.utils import timezone
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
import os
from decouple import config
import csv

def home_view(request):
    return HttpResponse("Welcome to the Stock Prediction App")

def fetch_stock_data(request):
    API_KEY = config('ALPHA_VANTAGE_API_KEY')
    symbol = 'AAPL'
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={API_KEY}'

    response = requests.get(url)
    data = response.json()

    if 'Time Series (Daily)' not in data:
        return render(request, 'error.html', {'error': 'Failed to fetch stock data'})

    time_series = data['Time Series (Daily)']

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

            writer.writerow([date, open_price, high_price, low_price, close_price, volume])

    return render(request, 'success.html', {'message': 'Stock data fetched and saved successfully!'})

def backtest_strategy(request):
    if request.method == 'POST':
        form = BacktestForm(request.POST)
        if form.is_valid():
            stock_symbol = form.cleaned_data['stock_symbol']
            initial_investment = Decimal(form.cleaned_data['initial_investment'])
            short_ma = form.cleaned_data['short_moving_avg']
            long_ma = form.cleaned_data['long_moving_avg']
            form_buy_price = form.cleaned_data.get('buy_price')
            form_sell_price = form.cleaned_data.get('sell_price')

            stock_data = StockData.objects.filter(symbol=stock_symbol).order_by('date')
            df = pd.DataFrame(list(stock_data.values('date', 'open_price', 'close_price', 'high_price', 'low_price', 'volume')))
            df.set_index('date', inplace=True)

            for column in ['close_price', 'open_price', 'high_price', 'low_price', 'volume']:
                df[column] = df[column].astype(float).apply(Decimal)

            df['short_ma'] = df['close_price'].rolling(window=min(short_ma, len(df))).mean()
            df['long_ma'] = df['close_price'].rolling(window=min(long_ma, len(df))).mean()

            if df.empty or len(df) < max(short_ma, long_ma):
                raise ValueError("Not enough data to calculate moving averages.")

            df['cash'] = initial_investment
            df['shares'] = Decimal(0.0)
            df['portfolio_value'] = initial_investment

            peak_portfolio_value = initial_investment
            max_drawdown = Decimal(0)
            total_trades = 0

            df['position'] = (df['short_ma'] > df['long_ma']).astype(int)

            for i in range(1, len(df)):
                current_date = df.index[i]
                previous_date = df.index[i - 1]

                current_price = Decimal(df.loc[current_date, 'close_price'])

                df.loc[current_date, 'portfolio_value'] = df.loc[previous_date, 'cash'] + (df.loc[previous_date, 'shares'] * current_price)

                peak_portfolio_value = max(peak_portfolio_value, df.loc[current_date, 'portfolio_value'])

                if peak_portfolio_value > 0:
                    drawdown = (peak_portfolio_value - df.loc[current_date, 'portfolio_value']) / peak_portfolio_value * 100
                    max_drawdown = max(max_drawdown, drawdown)
                else:
                    drawdown = Decimal(0)

                if df.loc[current_date, 'position'] == 1 and df.loc[previous_date, 'position'] == 0:
                    if current_price <= form_buy_price:
                        shares_to_buy = df.loc[previous_date, 'cash'] // current_price
                        total_cost = shares_to_buy * current_price

                        if df.loc[previous_date, 'cash'] >= total_cost:
                            df.loc[current_date, 'shares'] = df.loc[previous_date, 'shares'] + shares_to_buy
                            df.loc[current_date, 'cash'] = df.loc[previous_date, 'cash'] - total_cost
                            total_trades += 1

                            df.loc[current_date, 'portfolio_value'] = df.loc[current_date, 'cash'] + (df.loc[current_date, 'shares'] * current_price)
                        else:
                            print(f"Insufficient funds to buy on {current_date}. Cash available: {df.loc[previous_date, 'cash']}, Total cost: {total_cost}")
                    else:
                        print(f"No buy action on {current_date}, as price {current_price} exceeds buy price {form_buy_price}")

                elif df.loc[current_date, 'position'] == 0 and df.loc[previous_date, 'position'] == 1:
                    if current_price >= form_sell_price:
                        sell_price = current_price
                        df.loc[current_date, 'cash'] = df.loc[previous_date, 'cash'] + (sell_price * df.loc[previous_date, 'shares'])
                        df.loc[current_date, 'shares'] = Decimal(0.0)
                        total_trades += 1

                        df.loc[current_date, 'portfolio_value'] = df.loc[current_date, 'cash']
                    else:
                        print(f"No sell action on {current_date}, as price {current_price} is below sell price {form_sell_price}")


            final_portfolio_value = df['portfolio_value'].iloc[-1]
            total_return = ((final_portfolio_value - initial_investment) / initial_investment) * 100

            return render(request, 'backtest_result.html', {
                'total_return': total_return,
                'max_drawdown': max_drawdown,
                'num_trades': total_trades
            })
    else:
        form = BacktestForm()

    return render(request, 'backtest.html', {'form': form})


base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

model_path = os.path.join(base_dir, 'linear_regression_model.pkl')

with open(model_path, 'rb') as f:
    model = joblib.load(f)
    print(f"Loaded model: {model}")
    print(f"Type of model: {type(model)}")

def predict_stock_prices(symbol):
    stock_data = StockData.objects.filter(symbol=symbol).order_by('date')

    if not stock_data.exists():
        return None

    dates = np.array([stock.date for stock in stock_data])
    close_prices = np.array([stock.close_price for stock in stock_data])

    X = np.array([date.toordinal() for date in dates]).reshape(-1, 1)

    last_date = dates[-1]
    future_dates = [last_date + timedelta(days=i) for i in range(1, 31)]
    X_future = np.array([date.toordinal() for date in future_dates]).reshape(-1, 1)

    predicted_prices = model.predict(X_future)

    for date, predicted_price in zip(future_dates, predicted_prices):
        PredictedStockData.objects.update_or_create(
            symbol=symbol,
            date=date,
            defaults={'predicted_price': predicted_price}
        )

    return predicted_prices, future_dates

def stock_price_predictions(request, symbol):
    predictions, future_dates = predict_stock_prices(symbol)

    if predictions is None:
        return JsonResponse({'error': 'No historical data found for symbol: {}'.format(symbol)})

    response_data = {
        'symbol': symbol,
        'predictions': [{'date': date, 'predicted_price': price} for date, price in zip(future_dates, predictions)]
    }

    return JsonResponse(response_data)

def view_predictions(request, symbol):
    predictions = PredictedStockData.objects.filter(symbol=symbol).order_by('date')
    
    return render(request, 'predictions.html', {'predictions': predictions})

def report_view(request, symbol):
    metrics, plot_image = generate_report(symbol)

    if request.GET.get('format') == 'json':
        return JsonResponse({
            'symbol': symbol,
            'metrics': metrics
        })

    elif request.GET.get('format') == 'pdf':
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{symbol}_report.pdf"'

        c = canvas.Canvas(response, pagesize=letter)
        c.drawString(100, 750, f'Performance Report for {symbol}')
        c.drawString(100, 730, f"Mean Actual Price: {metrics['Mean Actual Price']:.2f}")
        c.drawString(100, 710, f"Mean Predicted Price: {metrics['Mean Predicted Price']:.2f}")
        c.drawString(100, 690, f"Actual Price Standard Deviation: {metrics['Actual Price Standard Deviation']:.2f}")
        c.drawString(100, 670, f"Predicted Price Standard Deviation: {metrics['Predicted Price Standard Deviation']:.2f}")

        c.drawImage(ImageReader(plot_image), 50, 400, width=500, height=300)
        c.showPage()
        c.save()

        return response

    return render(request, 'report.html', {'metrics': metrics, 'plot_image': plot_image})