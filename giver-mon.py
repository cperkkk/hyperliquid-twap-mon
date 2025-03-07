import json
import time
import sqlite3
import os
from websocket import create_connection, WebSocketConnectionClosedException

# Database setup (assuming SQLite)
conn = sqlite3.connect('positions.db')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS positions
                (coin TEXT PRIMARY KEY, position_size REAL)''')
conn.commit()

def create_websocket_connection():
    """Create a new WebSocket connection and send subscription"""
    ws = create_connection("wss://api-ui.hyperliquid.xyz/ws")
    message = {
        "method": "subscribe",
        "subscription": {
            "type": "webData2",
            "user": "0x8fc7c0442e582bca195978c5a4fdec2e7c5bb0f7"
        }
    }
    ws.send(json.dumps(message))
    return ws


giver_longing = None
def handle_position_data(data):
    global giver_longing
    """Process position data and update database"""
    asset_positions = data["data"]["clearinghouseState"]["assetPositions"]
    
    coin_list = ["BTC", "XRP", "ETH", "SOL", "ADA", "HYPE"]
    d = dict()
    for position in asset_positions:
        coin = position["position"]["coin"]
        d[coin] = 1
    
    for i in coin_list:
        if i not in d:
            asset_positions.append(
                {
                    'position': {
                        'coin': i,
                        'szi': 0,
                    }
                }
            )
    

    for position in asset_positions:
        coin = position["position"]["coin"]

        if coin in coin_list:
            szi = float(position["position"]["szi"])
            
            cursor.execute("SELECT position_size FROM positions WHERE coin = ?", (coin,))
            result = cursor.fetchone()
            old_size = result[0] if result else 0
            
            if szi != old_size:
                # Your notification logic here
                if old_size == 0 and szi != 0:
                    print(f"New position opened for {coin} with size {szi}")
                else:
                    print(f"Position for {coin} changed from {old_size} to {szi}")
                    if old_size > szi:
                        if giver_longing == True or giver_longing == None:
                            os.popen('paplay mmixkit-classic-alarm-995.wav').read()
                        giver_longing = False
                    else:
                        if giver_longing == False or giver_longing == None:
                            os.popen('paplay mixkit-rooster-crowing-in-the-morning-2462.wav').read()
                        giver_longing = True
                
                cursor.execute("INSERT OR REPLACE INTO positions (coin, position_size) VALUES (?, ?)", 
                             (coin, szi))
                conn.commit()
                

def websocket_listener():
    reconnect_interval = 1  # Start with 1 second reconnect delay
    max_reconnect_interval = 60  # Maximum 60 seconds between retries
    
    while True:
        ws = None
        try:
            # Create connection with exponential backoff
            ws = create_websocket_connection()
            reconnect_interval = 1  # Reset reconnect interval on success
            
            while True:
                try:
                    response = ws.recv()
                    data = json.loads(response)
                  
                    if 'clearinghouseState' in data.get('data', {}):
                        handle_position_data(data)
                        
                except WebSocketConnectionClosedException:
                    print("Connection closed, reconnecting...")
                    break
                except json.JSONDecodeError as e:
                    print(f"JSON decode error: {e}")
                except KeyError as e:
                    print(f"Missing expected key in data: {e}")
                except Exception as e:
                    print(f"Unexpected error: {e}")
                    break

        except Exception as e:
            print(f"Connection error: {e}")
        
        finally:
            if ws:
                try:
                    ws.close()
                except:
                    pass
        
        # Exponential backoff with max limit
        print(f"Reconnecting in {reconnect_interval} seconds...")
        time.sleep(reconnect_interval)
        reconnect_interval = min(reconnect_interval * 2, max_reconnect_interval)

if __name__ == "__main__":
    websocket_listener()
