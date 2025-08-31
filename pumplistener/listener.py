import asyncio
import websockets
import json
import time

# --- CONFIGURATION ---
PUMPORTAL_WSS = "wss://pumpportal.fun/api/data"

async def pump_fun_listener():
    """
    Connects to the PumpPortal WebSocket, listens for new token events,
    and prints the data for every creation event.
    """
    print("🚀 Starting Basic Pump.fun New Token Monitor...")
    print(f"Connecting to WebSocket: {PUMPORTAL_WSS}")

    try:
        async with websockets.connect(PUMPORTAL_WSS) as websocket:
            print("✅ Successfully connected to WebSocket.")
            subscribe_message = {"method": "subscribeNewToken"}
            await websocket.send(json.dumps(subscribe_message))
            print("✅ Subscribed to new token stream. Waiting for launches...\n")

            while True:
                try:
                    message = await websocket.recv()
                    data = json.loads(message)

                    if data and data.get('txType') == 'create':
                        print("=============================================")
                        print(f"🔥 New Token Creation Detected!")
                        print(f"   -> Name: {data.get('name', 'N/A')} (${data.get('symbol', 'N/A')})")
                        print(f"   -> Mint Address: {data.get('mint', 'N/A')}")
                        print(f"   -> Creator Invested: {data.get('solAmount', 0):.2f} SOL")
                        print(f"   -> Creator: {data.get('traderPublicKey', 'N/A')}")
                        print(f"   -> Link: https://pump.fun/{data.get('mint', '')}")
                        print("=============================================\n")

                except websockets.ConnectionClosed:
                    print("⚠️ WebSocket connection closed. Will attempt to reconnect...")
                    break
                except Exception as e:
                    print(f"💥 An error occurred while processing a message: {e}")

    except Exception as e:
        print(f"💥 Failed to connect to WebSocket: {e}")

def run_listener_in_new_loop():
    """
    Wrapper to run the async listener in a new asyncio event loop.
    This is necessary to run in a separate thread.
    """
    while True:
        try:
            # Create and run a new event loop for the async function
            asyncio.run(pump_fun_listener())
        except Exception as e:
            print(f"💥 Main listener loop crashed: {e}")
        
        print("Reconnecting in 10 seconds...")
        time.sleep(10)