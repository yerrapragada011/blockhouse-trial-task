from django.urls import path
from .views import fetch_stock_data, backtest_strategy

urlpatterns = [
    path('fetchfinancialdata/', fetch_stock_data, name='fetch_stock_data'),
    path('backtest/', backtest_strategy, name='backtest_strategy'),
]
