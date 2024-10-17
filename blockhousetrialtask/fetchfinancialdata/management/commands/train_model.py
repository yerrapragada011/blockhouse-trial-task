from django.core.management.base import BaseCommand
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import joblib

class Command(BaseCommand):
    help = 'Train and save the linear regression model'

    def handle(self, *args, **kwargs):
        # Load your historical stock price data
        data = pd.read_csv('stock_data.csv')  # Replace with your data source

        # Prepare the features and target variable
        data['Date'] = pd.to_datetime(data['Date'])
        data['Days'] = (data['Date'] - data['Date'].min()).dt.days

        X = data[['Days']]
        y = data['Close']

        # Split the data into training and testing sets
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Train the model
        model = LinearRegression()
        model.fit(X_train, y_train)

        # Save the model to a .pkl file
        joblib.dump(model, 'linear_regression_model.pkl')

        self.stdout.write(self.style.SUCCESS('Model trained and saved successfully!'))
