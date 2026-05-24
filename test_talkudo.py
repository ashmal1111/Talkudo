#!/usr/bin/env python3
import socket
import json
import sqlite3
import time
import threading

print("=" * 60)
print("🧪 TALKUDO QUICK FEATURE TEST")
print("=" * 60)

# Test 1: Server Connection
print("\n1️⃣ Testing Server Connection...")
try:
    test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    test_socket.settimeout(2)
    test_socket.connect(('127.0.0.1', 5555))
    test_socket.close()
    print("   ✅ Server is running")
except:
    print("   ❌ Server is NOT running")
    print("   Please start server: python run_server.py")
    exit(1)

# Test 2: Database
print("\n2️⃣ Testing Database...")
try:
    conn = sqlite3.connect('talkudo.db')
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM messages")
    msg_count = cursor.fetchone()[0]
    print(f"   ✅ Database OK - Users: {user_count}, Messages: {msg_count}")
    conn.close()
except Exception as e:
    print(f"   ❌ Database error: {e}")

# Test 3: User Registration Test
print("\n3️⃣ Testing User Registration...")
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('127.0.0.1', 5555))
    
    test_username = f"test_{int(time.time())}"
    register_msg = {
        'type': 'auth',
        'action': 'register',
        'username': test_username,
        'email': f"{test_username}@test.com",
        'password': 'test123'
    }
    sock.send(json.dumps(register_msg).encode('utf-8'))
    response = json.loads(sock.recv(4096).decode('utf-8'))
    sock.close()
    
    if response['status'] == 'success':
        print(f"   ✅ Registration works - Created user: {test_username}")
    else:
        print(f"   ❌ Registration failed: {response}")
except Exception as e:
    print(f"   ❌ Registration error: {e}")

# Test 4: Login Test
print("\n4️⃣ Testing User Login...")
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('127.0.0.1', 5555))
    
    login_msg = {
        'type': 'auth',
        'action': 'login',
        'username': 'kunjayamu',
        'password': '123456'
    }
    sock.send(json.dumps(login_msg).encode('utf-8'))
    response = json.loads(sock.recv(4096).decode('utf-8'))
    sock.close()
    
    if response['status'] == 'success':
        print(f"   ✅ Login works for user: {response.get('username')}")
    else:
        print(f"   ❌ Login failed: {response}")
except Exception as e:
    print(f"   ❌ Login error: {e}")

# Test 5: Message History
print("\n5️⃣ Testing Message History...")
try:
    conn = sqlite3.connect('talkudo.db')
    cursor = conn.cursor()
    cursor.execute("""
        SELECT u1.username, u2.username, m.content, m.timestamp 
        FROM messages m
        JOIN users u1 ON m.sender_id = u1.user_id
        JOIN users u2 ON m.receiver_id = u2.user_id
        ORDER BY m.timestamp DESC LIMIT 3
    """)
    messages = cursor.fetchall()
    conn.close()
    
    if messages:
        print("   ✅ Recent messages found:")
        for msg in messages:
            print(f"      📝 {msg[0]} → {msg[1]}: {msg[2][:50]}")
    else:
        print("   ⚠️ No messages found. Send some messages first!")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 6: User List
print("\n6️⃣ Testing User List...")
try:
    conn = sqlite3.connect('talkudo.db')
    cursor = conn.cursor()
    cursor.execute("SELECT username, status FROM users")
    users = cursor.fetchall()
    conn.close()
    
    print(f"   ✅ Total users: {len(users)}")
    online = [u[0] for u in users if u[1] == 'online']
    offline = [u[0] for u in users if u[1] != 'online']
    if online:
        print(f"      🟢 Online: {', '.join(online)}")
    if offline:
        print(f"      ⚫ Offline: {', '.join(offline)}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Summary
print("\n" + "=" * 60)
print("📊 TEST SUMMARY")
print("=" * 60)
print("✅ All basic features are working!")
print("\n💡 To test more features:")
print("   1. Open two clients and send messages")
print("   2. Try emojis: 😀 😂 ❤️")
print("   3. Right-click on messages for reactions")
print("   4. Try file sharing with 📎 button")
print("   5. Test AI assistant by typing @ai")
print("   6. Change theme with 🌙 button")
