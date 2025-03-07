import json
import sqlite3
import os
from websocket import create_connection

# Set up SQLite database
conn = sqlite3.connect('positions.db')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS positions
                 (coin TEXT PRIMARY KEY, position_size REAL)''')
conn.commit()

# Create WebSocket connection
ws = create_connection("wss://api-ui.hyperliquid.xyz/ws")

# Prepare the message
message = {
    "method": "subscribe",
    "subscription": {
        "type": "webData2",
        "user": "0x8fc7c0442e582bca195978c5a4fdec2e7c5bb0f7"
    }
}

# Send the message
ws.send(json.dumps(message))

# Keep listening for responses
try:
    while True:
        response = ws.recv()
        data = json.loads(response)
        if 'clearinghouseState' in data['data']:
            # Extract asset positions
            asset_positions = data["data"]["clearinghouseState"]["assetPositions"]
            
            # Process each position
            for position in asset_positions:
                coin = position["position"]["coin"]
                if coin in ["BTC", "XRP", "ETH", "SOL", "ADA"]:
                    szi = float(position["position"]["szi"])
                    
                    # Get the previous position size from the database
                    cursor.execute("SELECT position_size FROM positions WHERE coin = ?", (coin,))
                    result = cursor.fetchone()
                    old_size = result[0] if result else 0
                    
                    # Compare and detect changes
                    if szi != old_size:
                        if old_size == 0 and szi != 0:
                            print(f"New position opened for {coin} with size {szi}")
                            os.popen('paplay mixkit-rooster-crowing-in-the-morning-2462.wav').read()
                        elif old_size != 0 and szi == 0:
                            print(f"Position for {coin} closed")
                            os.popen('paplay mixkit-rooster-crowing-in-the-morning-2462.wav').read()
                        else:
                            print(f"Position for {coin} changed from {old_size} to {szi}")
                            os.popen('paplay mixkit-rooster-crowing-in-the-morning-2462.wav').read()
                        
                        # Update the database
                        cursor.execute("INSERT OR REPLACE INTO positions (coin, position_size) VALUES (?, ?)", (coin, szi))
                        conn.commit()

finally:
    ws.close()
    conn.close()
