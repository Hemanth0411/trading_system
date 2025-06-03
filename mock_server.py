import asyncio
import websockets
import json
import random
from datetime import datetime, timezone

# Server settings
HOST = 'localhost'
PORT = 8765  # Default WebSocket port
TICKERS = ["MOCKSTOCK_A", "MOCKSTOCK_B", "MOCKSTOCK_C"] # Stocks we'll pretend to track
# Start with some random prices for our mock stocks
INITIAL_PRICES = {ticker: random.uniform(50, 200) for ticker in TICKERS}
# How much the price can wiggle each update
PRICE_FLUCTUATION_RANGE = 0.5
# How often to send out new prices (in seconds)
UPDATE_INTERVAL_SECONDS = 2

# Keep track of who's connected
connected_clients = set()

async def send_stock_updates(websocket):
    """
    This function runs for each client that connects.
    Its main job here is to manage the 'connected_clients' set.
    """
    print(f"Client {websocket.remote_address} connected.")
    connected_clients.add(websocket) # Add new client to our set
    try:
        # Just keep the connection alive. The actual data sending is done by 'broadcast_prices'.
        while True:
            await asyncio.sleep(0.1) # Small sleep to allow other things to run
            # If we needed to receive messages from clients, we'd use `await websocket.recv()` here.
    except websockets.exceptions.ConnectionClosedOK:
        print(f"Client {websocket.remote_address} disconnected gracefully.")
    except websockets.exceptions.ConnectionClosedError as e:
        print(f"Client {websocket.remote_address} connection error: {e}")
    finally:
        connected_clients.remove(websocket) # Remove client when they disconnect
        print(f"Client {websocket.remote_address} removed.")


async def broadcast_prices():
    """
    This runs in the background, making up new prices and sending them to everyone.
    """
    global INITIAL_PRICES # We'll be changing these prices
    while True:
        await asyncio.sleep(UPDATE_INTERVAL_SECONDS) # Wait before sending next batch of prices
        if not connected_clients: # No one listening? Don't bother.
            continue

        updates = [] # Collect all stock updates for this interval
        for ticker in TICKERS:
            # Make the price change a little bit, up or down
            change = random.uniform(-PRICE_FLUCTUATION_RANGE, PRICE_FLUCTUATION_RANGE)
            INITIAL_PRICES[ticker] = max(0.01, INITIAL_PRICES[ticker] + change) # Price can't go below 0.01

            update_data = {
                "ticker": ticker,
                "price": round(INITIAL_PRICES[ticker], 2), # Round to 2 decimal places
                "timestamp": datetime.now(timezone.utc).isoformat() # Current time in UTC
            }
            updates.append(update_data)

        message_to_send = json.dumps(updates) # Convert list of updates to a JSON string

        # Send the message to all connected clients
        # We copy the set in case it changes while we're sending (e.g., a client disconnects)
        tasks = [client.send(message_to_send) for client in list(connected_clients)]
        if tasks:
            # 'asyncio.gather' sends all messages more or less at the same time
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    # Something went wrong sending to one client (maybe they just disconnected)
                    # We'll just ignore it for now, the 'send_stock_updates' handler will clean them up.
                    pass

async def main():
    # Start the price broadcasting task so it runs in the background
    asyncio.create_task(broadcast_prices())

    print(f"Mock WebSocket server starting on ws://{HOST}:{PORT}")
    # Start the actual WebSocket server and keep it running forever
    async with websockets.serve(send_stock_updates, HOST, PORT):
        await asyncio.Future()  # This basically means "run until stopped"

if __name__ == "__main__":
    try:
        asyncio.run(main()) # Start the server
    except KeyboardInterrupt:
        print("Server shutting down...") # For Ctrl+C