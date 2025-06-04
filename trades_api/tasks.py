from celery import shared_task
import time 

@shared_task
def send_trade_notification_task(trade_details):

    print(f"TASK STARTED: Preparing to send notification for trade: {trade_details}")
    
    # Simulate some work (e.g., calling an external email service)
    time.sleep(5) # Simulate a 5-second delay
    
    print(f"TASK COMPLETED: Notification 'sent' for trade: {trade_details}")
    return f"Notification processed for {trade_details.get('id', 'N/A')}"