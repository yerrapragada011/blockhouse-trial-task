from django.urls import path
from .views import fetch_stock_data

urlpatterns = [
    path('fetch-stock-data/', fetch_stock_data, name='fetch_stock_data'),
]
