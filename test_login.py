import socket
import json

print("Testing login with your actual users...")
print("-" * 50)

# Get users from database
import sqlite3
conn = sqlite3.connect('talkudo.db')
cursor = conn.cursor()
cursor.execute("SELECT user_id, username FROM users WHERE username NOT LIKE 'test_%'")
users = cursor.fetchall()
conn.close()

for user_id, username in users:
    print(f"\nTesting user: {username}")
    print("Please enter the password you used when registering:")
    password = input(f"Password for {username}: ")
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('127.0.0.1', 5555))
        
        login_msg = {
            'type': 'auth',
            'action': 'login',
            'username': username,
            'password': password
        }
        sock.send(json.dumps(login_msg).encode('utf-8'))
        response = json.loads(sock.recv(4096).decode('utf-8'))
        sock.close()
        
        if response['status'] == 'success':
            print(f"   ✅ Login successful for {username}!")
        else:
            print(f"   ❌ Login failed for {username}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
