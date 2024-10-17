from django.urls import path
from .views import fetch_stock_data, backtest_strategy, stock_price_predictions, view_predictions

urlpatterns = [
    path('fetchfinancialdata/', fetch_stock_data, name='fetch_stock_data'),
    path('backtest/', backtest_strategy, name='backtest_strategy'),
    path('predict/<str:symbol>/', stock_price_predictions, name='stock_price_predictions'),
    path('view_predictions/<str:symbol>/', view_predictions, name='view_predictions'),
]
