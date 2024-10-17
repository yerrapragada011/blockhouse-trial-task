from django import forms

class BacktestForm(forms.Form):
    stock_symbol = forms.CharField(label='Stock Symbol', max_length=10)
    initial_investment = forms.DecimalField(label='Initial Investment', max_digits=10, decimal_places=2)
    short_moving_avg = forms.IntegerField(label='Short Moving Average (e.g., 50 days)')
    long_moving_avg = forms.IntegerField(label='Long Moving Average (e.g., 200 days)')
    buy_price = forms.DecimalField(label='Buy Price', decimal_places=2, max_digits=10, required=False)
    sell_price = forms.DecimalField(label='Sell Price', decimal_places=2, max_digits=10, required=False)