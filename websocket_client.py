import asyncio
import websockets
import json
from datetime import datetime, timedelta, timezone

SERVER_URL = "ws://localhost:8765"
PRICE_HISTORY_SECONDS = 60  # How long we look back for the price check (1 minute)
PRICE_INCREASE_THRESHOLD_PERCENT = 2.0 # The 2% jump we're looking for

# This dictionary will hold lists of (timestamp, price) for each stock ticker
# e.g., {"AAPL": [(datetime_obj, 150.00), (datetime_obj, 150.10)], ...}
recent_prices = {}

def update_and_check_price_history(ticker, current_price, current_timestamp_dt):
    """
    Updates the price history for a ticker and checks for a >2% increase in the last minute.
    Returns a notification message if the threshold is met, otherwise None.
    """
    if ticker not in recent_prices:
        recent_prices[ticker] = [] # Start a new list if it's a new ticker

    # Add the latest price and time to our list for this stock
    recent_prices[ticker].append((current_timestamp_dt, current_price))

    # Figure out what time it was one minute ago
    one_minute_ago = current_timestamp_dt - timedelta(seconds=PRICE_HISTORY_SECONDS)

    # Keep only the prices from the last minute to prevent the list from growing forever
    valid_history = []
    for ts, price in recent_prices[ticker]:
        if ts >= one_minute_ago:
            valid_history.append((ts, price))
    recent_prices[ticker] = valid_history

    # Need at least two prices in the last minute to compare (an old one and the current one)
    if not recent_prices[ticker] or len(recent_prices[ticker]) < 2:
        return None

    # The first price in our 'valid_history' is the oldest one from the last minute
    earliest_ts_in_window, earliest_price_in_window = recent_prices[ticker][0]

    if current_price > earliest_price_in_window:
        # Calculate the percentage increase
        percentage_increase = ((current_price - earliest_price_in_window) / earliest_price_in_window) * 100

        if percentage_increase > PRICE_INCREASE_THRESHOLD_PERCENT:
            notification = (
                f"ALERT! {ticker} increased by {percentage_increase:.2f}% "
                f"(from {earliest_price_in_window:.2f} at {earliest_ts_in_window.strftime('%H:%M:%S')} "
                f"to {current_price:.2f} at {current_timestamp_dt.strftime('%H:%M:%S')}) "
                f"within the last {PRICE_HISTORY_SECONDS} seconds."
            )
            return notification
    return None


async def connect_and_listen():
    """
    Connects to the WebSocket server, prints received messages,
    and monitors for significant price increases.
    """
    try:
        async with websockets.connect(SERVER_URL) as websocket: # Try to connect
            print(f"Successfully connected to server at {SERVER_URL}")

            while True: # Keep listening for messages forever (or until disconnect)
                try:
                    message_str = await websocket.recv() # Wait for a message from server
                    updates = json.loads(message_str) # Server sends JSON, so parse it

                    print(f"\nReceived {len(updates)} updates:", flush=True)

                    for update_data in updates:
                        ticker = update_data['ticker']
                        price = float(update_data['price']) # Make sure price is a number
                        # Convert timestamp string from server to a real datetime object
                        timestamp_dt = datetime.fromisoformat(update_data['timestamp'].replace('Z', '+00:00'))

                        print(f"  Ticker: {ticker}, Price: {price:.2f}, Timestamp: {timestamp_dt.strftime('%Y-%m-%d %H:%M:%S')}", flush=True)

                        # Check if this new price triggers our 2% rule
                        notification = update_and_check_price_history(ticker, price, timestamp_dt)
                        if notification:
                            print(f"\n>> {notification}\n", flush=True) # Show the alert!

                except websockets.exceptions.ConnectionClosedOK:
                    print("Connection closed gracefully by the server.")
                    break # Exit the loop if server closes connection
                except websockets.exceptions.ConnectionClosedError as e:
                    print(f"Connection closed with error: {e}")
                    break # Exit loop on error too
                except json.JSONDecodeError:
                    # Just in case server sends something weird that's not JSON
                    print(f"Received a non-JSON message: {message_str}", flush=True)
                except Exception as e:
                    print(f"An unexpected error occurred: {e}", flush=True)
                    break # Stop if something else unexpected happens

    except ConnectionRefusedError:
        # This happens if the server script isn't running
        print(f"Connection refused. Is the server running at {SERVER_URL}?")
    except Exception as e:
        print(f"Failed to connect or an error occurred: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(connect_and_listen()) # Start the client
    except KeyboardInterrupt:
        print("\nClient shutting down...") # For Ctrl+C