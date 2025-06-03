from rest_framework import serializers
from .models import Trade
import re # For regular expression (used in ticker validation)

# Serializers turn our 'Trade' model data into JSON (and vice-versa)
# and also handle validation of incoming data.
class TradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trade # This serializer is for our Trade model
        # These are the fields that will be included in the API
        fields = ['id', 'ticker', 'price', 'quantity', 'side', 'timestamp']
        # Alternatively, `fields = '__all__'` would include all fields from the model.

    # Custom validation for the 'price' field.
    # DRF automatically calls methods named 'validate_<field_name>'.
    def validate_price(self, value):
        """
        Check that the price is not negative.
        """
        if value < 0:
            raise serializers.ValidationError("Price cannot be negative.")
        return value

    # Custom validation for the 'quantity' field
    def validate_quantity(self, value):
        """
        Check that the quantity is not negative.
        """
        if value < 0:
            raise serializers.ValidationError("Quantity cannot be negative.")
        return value

    # Custom validation for the 'ticker' field
    def validate_ticker(self, value):
        """
        Check that the ticker is uppercase and between 1 to 5 characters.
        e.g. "AAPL" is good, "aapl" or "APPLE123" is bad.
        """
        # Regex: ^ means start, [A-Z] means uppercase letter, {1,5} means 1 to 5 times, $ means end.
        if not re.match(r"^[A-Z]{1,5}$", value):
            raise serializers.ValidationError(
                "Ticker must be 1-5 uppercase letters (e.g., AAPL, TSLA)."
            )
        return value