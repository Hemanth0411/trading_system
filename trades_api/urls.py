from django.urls import path
from .views import TradeListCreateView # Importing our view

urlpatterns = [
    # This maps the URL 'trades/' to our TradeListCreateView.
    # So, requests to /api/trades/ (assuming '/api/' is the prefix in project urls)
    # will be handled by this view.
    path('trades/', TradeListCreateView.as_view(), name='trade-list-create'),
]