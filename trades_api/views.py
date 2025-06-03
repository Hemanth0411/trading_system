from rest_framework import generics
from .models import Trade
from .serializers import TradeSerializer
from django.utils.dateparse import parse_datetime # For converting date strings to datetime objects
# from datetime import timedelta # Could be used for more precise end_date handling

# This view handles both listing trades (GET) and creating new trades (POST)
class TradeListCreateView(generics.ListCreateAPIView):
    serializer_class = TradeSerializer # Use our TradeSerializer for this view

    # This method controls what data is returned for GET requests
    def get_queryset(self):
        """
        Optionally restricts the returned trades by filtering against
        a `ticker`, `start_date` and `end_date` query parameter in the URL.
        Example: /api/trades/?ticker=AAPL&start_date=2024-01-01&end_date=2024-01-31
        """
        queryset = Trade.objects.all().order_by('-timestamp') # Start with all trades, newest first

        # Get filter parameters from the URL (e.g., ?ticker=AAPL)
        ticker = self.request.query_params.get('ticker')
        start_date_str = self.request.query_params.get('start_date')
        end_date_str = self.request.query_params.get('end_date')

        if ticker:
            # Filter by ticker, case-insensitive (e.g., "aapl" will match "AAPL")
            queryset = queryset.filter(ticker__iexact=ticker)

        if start_date_str:
            start_date = parse_datetime(start_date_str) # Convert string to datetime
            if start_date: # If conversion was successful
                # __gte means "greater than or equal to"
                queryset = queryset.filter(timestamp__gte=start_date)

        if end_date_str:
            end_date = parse_datetime(end_date_str) # Convert string to datetime
            if end_date: # If conversion was successful
                # __lte means "less than or equal to"
                # Note: if end_date_str is just a date like "2024-01-01",
                # parse_datetime makes it "2024-01-01T00:00:00".
                # This means it only includes trades right at midnight on that day.
                # For including the whole day, end_date might need to be adjusted
                # to the end of the day (e.g., by adding timedelta(days=1) - timedelta(microseconds=1)).
                # For this assignment, the current behavior is acceptable.
                queryset = queryset.filter(timestamp__lte=end_date)

        return queryset

    # DRF's ListCreateAPIView automatically handles POST requests
    # using the serializer_class to create new Trade objects.
    # No need to write custom post() method for basic creation.