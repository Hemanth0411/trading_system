from rest_framework import generics, status
from .models import Trade
from .serializers import TradeSerializer
from django.utils.dateparse import parse_datetime # For converting date strings to datetime objects
from .tasks import send_trade_notification_task
# from datetime import timedelta # Could be used for more precise end_date handling

# This view handles both listing trades (GET) and creating new trades (POST)
class TradeListCreateView(generics.ListCreateAPIView):
    serializer_class = TradeSerializer # Use our TradeSerializer for this view

    # This method controls what data is returned for GET requests
    def get_queryset(self):
        
        queryset = Trade.objects.all().order_by('-timestamp')
        ticker = self.request.query_params.get('ticker')
        start_date_str = self.request.query_params.get('start_date')
        end_date_str = self.request.query_params.get('end_date')
        if ticker:
            queryset = queryset.filter(ticker__iexact=ticker)
        if start_date_str:
            start_date = parse_datetime(start_date_str)
            if start_date:
                queryset = queryset.filter(timestamp__gte=start_date)
        if end_date_str:
            end_date = parse_datetime(end_date_str)
            if end_date:
                queryset = queryset.filter(timestamp__lte=end_date)
        return queryset

    def perform_create(self, serializer):
        trade_instance = serializer.save() 

        # Prepare details for the task (serializer.data is a good source after save)
        # It's generally better to pass simple data types (like IDs or dicts) to Celery tasks
        # rather than full model instances, as model instances might not serialize well
        # or might carry too much state.
        trade_details_for_task = {
            'id': trade_instance.id,
            'ticker': trade_instance.ticker,
            'price': str(trade_instance.price), # Convert Decimal to string
            'quantity': trade_instance.quantity,
            'side': trade_instance.side,
            'timestamp': trade_instance.timestamp.isoformat() # Convert datetime to string
        }
        
        # Call the Celery task asynchronously
        # .delay() is a shortcut for .apply_async()
        send_trade_notification_task.delay(trade_details_for_task)
        
        print(f"API View: New trade {trade_instance.id} created. Notification task queued.")