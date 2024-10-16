from django.shortcuts import render

# Create your views here.

import requests
from decouple import config

# Get the API key from environment variables
API_KEY = config('ALPHA_VANTAGE_API_KEY')
symbol = 'AAPL'
url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={API_KEY}'

# Make the request
response = requests.get(url)
data = response.json()

# Check the data
print(data)
