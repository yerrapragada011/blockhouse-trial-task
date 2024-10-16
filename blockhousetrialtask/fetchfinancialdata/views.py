from django.shortcuts import render
import requests
from decouple import config
from django.http import JsonResponse

def fetch_stock_data(request):
    # Get the API key from environment variables
    API_KEY = config('ALPHA_VANTAGE_API_KEY')
    symbol = 'AAPL'
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={API_KEY}'

    # Make the request
    response = requests.get(url)
    data = response.json()

    # Return the data as a JSON response
    return JsonResponse(data)
