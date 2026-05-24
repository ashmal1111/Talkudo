import socket
import threading
import json
import hashlib
import secrets
import sqlite3
from datetime import datetime
from pathlib import Path
import sys
import os

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

class DatabaseManager:
    def __init__(self, db_path="talkudo.db"):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        return sqlite3.connect(self.db_path, check_same_thread=False)
    
    def init_database(self):
        """Initialize database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                display_name TEXT,
                avatar TEXT,
                status TEXT DEFAULT 'offline',
                last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                theme TEXT DEFAULT 'dark'
            )
        ''')
        
        # Messages table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                message_id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender_id INTEGER,
                receiver_id INTEGER,
                group_id INTEGER,
                message_type TEXT DEFAULT 'text',
                content TEXT,
                file_path TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_read INTEGER DEFAULT 0,
                is_delivered INTEGER DEFAULT 0,
                FOREIGN KEY (sender_id) REFERENCES users(user_id),
                FOREIGN KEY (receiver_id) REFERENCES users(user_id)
            )
        ''')
        
        # Groups table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS groups (
                group_id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_name TEXT NOT NULL,
                created_by INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (created_by) REFERENCES users(user_id)
            )
        ''')
        
        # Group members table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS group_members (
                group_id INTEGER,
                user_id INTEGER,
                role TEXT DEFAULT 'member',
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (group_id) REFERENCES groups(group_id),
                FOREIGN KEY (user_id) REFERENCES users(user_id),
                PRIMARY KEY (group_id, user_id)
            )
        ''')
        
        # User sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_sessions (
                session_id TEXT PRIMARY KEY,
                user_id INTEGER,
                login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def hash_password(self, password, salt=None):
        if not salt:
            salt = secrets.token_hex(16)
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        ).hex()
        return password_hash, salt
    
    def register_user(self, username, email, password):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT user_id FROM users WHERE username = ? OR email = ?", (username, email))
            if cursor.fetchone():
                conn.close()
                return False, "Username or email already exists"
            
            password_hash, salt = self.hash_password(password)
            
            cursor.execute('''
                INSERT INTO users (username, email, password_hash, salt, status)
                VALUES (?, ?, ?, ?, ?)
            ''', (username, email, password_hash, salt, 'offline'))
            
            conn.commit()
            user_id = cursor.lastrowid
            conn.close()
            
            return True, {"user_id": user_id, "username": username}
        except Exception as e:
            return False, str(e)
    
    def authenticate_user(self, username, password):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT user_id, username, password_hash, salt FROM users WHERE username = ? OR email = ?",
                (username, username)
            )
            user = cursor.fetchone()
            
            if not user:
                conn.close()
                return False, "Invalid credentials"
            
            user_id, username, stored_hash, salt = user
            
            password_hash, _ = self.hash_password(password, salt)
            
            if password_hash == stored_hash:
                cursor.execute("UPDATE users SET status = 'online', last_seen = ? WHERE user_id = ?",
                              (datetime.now(), user_id))
                conn.commit()
                conn.close()
                return True, {"user_id": user_id, "username": username}
            else:
                conn.close()
                return False, "Invalid credentials"
        except Exception as e:
            return False, str(e)
    
    def save_message(self, sender_id, receiver_id, content, message_type='text', group_id=None):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO messages (sender_id, receiver_id, group_id, message_type, content, timestamp, is_read, is_delivered)
                VALUES (?, ?, ?, ?, ?, ?, 0, 1)
            ''', (sender_id, receiver_id, group_id, message_type, content, datetime.now()))
            
            conn.commit()
            message_id = cursor.lastrowid
            conn.close()
            
            return message_id
        except Exception as e:
            print(f"Save message error: {e}")
            return None
    
    def get_message_history(self, user1_id, user2_id, limit=100):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT m.*, u.username as sender_name 
                FROM messages m
                JOIN users u ON m.sender_id = u.user_id
                WHERE (sender_id = ? AND receiver_id = ?) OR (sender_id = ? AND receiver_id = ?)
                ORDER BY timestamp DESC LIMIT ?
            ''', (user1_id, user2_id, user2_id, user1_id, limit))
            
            messages = cursor.fetchall()
            conn.close()
            
            # Convert to list of dicts
            result = []
            for msg in messages[::-1]:
                result.append({
                    'message_id': msg[0],
                    'sender_id': msg[1],
                    'receiver_id': msg[2],
                    'content': msg[4],
                    'timestamp': msg[6],
                    'sender_name': msg[9]
                })
            return result
        except Exception as e:
            print(f"Get history error: {e}")
            return []
    
    def get_online_users(self, current_user_id):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT user_id, username, status FROM users WHERE status = 'online' AND user_id != ?", (current_user_id,))
            users = cursor.fetchall()
            conn.close()
            
            return [{'user_id': u[0], 'username': u[1], 'status': u[2]} for u in users]
        except Exception as e:
            print(f"Get online users error: {e}")
            return []
    
    def get_all_users(self, current_user_id):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT user_id, username, status FROM users WHERE user_id != ?", (current_user_id,))
            users = cursor.fetchall()
            conn.close()
            
            return [{'user_id': u[0], 'username': u[1], 'status': u[2]} for u in users]
        except Exception as e:
            print(f"Get all users error: {e}")
            return []
    
    def update_user_status(self, user_id, status):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("UPDATE users SET status = ?, last_seen = ? WHERE user_id = ?",
                          (status, datetime.now(), user_id))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Update status error: {e}")
            return False

class ClientHandler:
    def __init__(self, client_socket, address, server):
        self.client_socket = client_socket
        self.address = address
        self.server = server
        self.user_id = None
        self.username = None
        self.db = DatabaseManager()
        self.running = True
    
    def handle(self):
        try:
            while self.running:
                data = self.client_socket.recv(4096).decode('utf-8')
                if not data:
                    break
                
                message = json.loads(data)
                self.process_message(message)
        except Exception as e:
            print(f"Client handler error: {e}")
        finally:
            self.disconnect()
    
    def process_message(self, message):
        msg_type = message.get('type')
        
        if msg_type == 'auth':
            self.authenticate(message)
        elif msg_type == 'message':
            self.handle_chat_message(message)
        elif msg_type == 'typing':
            self.handle_typing(message)
        elif msg_type == 'get_users':
            self.send_user_list()
        elif msg_type == 'get_history':
            self.send_message_history(message)
    
    def authenticate(self, message):
        action = message.get('action')
        
        if action == 'login':
            success, result = self.db.authenticate_user(
                message['username'],
                message['password']
            )
            
            if success:
                self.user_id = result['user_id']
                self.username = result['username']
                self.server.add_client(self.user_id, self)
                
                response = {
                    'type': 'auth',
                    'status': 'success',
                    'user_id': self.user_id,
                    'username': self.username
                }
                self.send(response)
                
                # Broadcast user online
                self.broadcast_status('online')
                
                # Send user list
                self.send_user_list()
            else:
                response = {
                    'type': 'auth',
                    'status': 'error',
                    'message': result
                }
                self.send(response)
        
        elif action == 'register':
            success, result = self.db.register_user(
                message['username'],
                message['email'],
                message['password']
            )
            
            response = {
                'type': 'auth',
                'action': 'register',
                'status': 'success' if success else 'error',
                'message': 'Registration successful' if success else result
            }
            self.send(response)
    
    def handle_chat_message(self, message):
        # Save to database
        message_id = self.db.save_message(
            self.user_id,
            message.get('receiver_id'),
            message.get('content'),
            message.get('message_type', 'text')
        )
        
        # Prepare message for delivery
        chat_message = {
            'type': 'message',
            'message_id': message_id,
            'sender_id': self.user_id,
            'sender_name': self.username,
            'content': message.get('content'),
            'timestamp': datetime.now().isoformat(),
            'message_type': message.get('message_type', 'text')
        }
        
        # Send to receiver
        receiver_id = message.get('receiver_id')
        receiver_handler = self.server.get_client(receiver_id)
        if receiver_handler:
            receiver_handler.send(chat_message)
            
            # Send delivery receipt
            receipt = {
                'type': 'delivery_receipt',
                'message_id': message_id,
                'status': 'delivered'
            }
            self.send(receipt)
    
    def handle_typing(self, message):
        receiver_id = message.get('receiver_id')
        receiver_handler = self.server.get_client(receiver_id)
        if receiver_handler:
            typing_msg = {
                'type': 'typing',
                'user_id': self.user_id,
                'username': self.username,
                'is_typing': message.get('is_typing', True)
            }
            receiver_handler.send(typing_msg)
    
    def broadcast_status(self, status):
        status_msg = {
            'type': 'status_update',
            'user_id': self.user_id,
            'username': self.username,
            'status': status,
            'timestamp': datetime.now().isoformat()
        }
        
        for client in self.server.get_all_clients().values():
            if client.user_id != self.user_id:
                client.send(status_msg)
    
    def send_user_list(self):
        users = self.db.get_all_users(self.user_id)
        response = {
            'type': 'user_list',
            'users': users
        }
        self.send(response)
    
    def send_message_history(self, message):
        other_user_id = message.get('other_user_id')
        history = self.db.get_message_history(self.user_id, other_user_id)
        
        response = {
            'type': 'message_history',
            'messages': history
        }
        self.send(response)
    
    def send(self, message):
        try:
            self.client_socket.send(json.dumps(message).encode('utf-8'))
        except Exception as e:
            print(f"Send error: {e}")
    
    def disconnect(self):
        if self.user_id:
            self.db.update_user_status(self.user_id, 'offline')
            self.server.remove_client(self.user_id)
            self.broadcast_status('offline')
        
        self.running = False
        try:
            self.client_socket.close()
        except:
            pass

class ChatServer:
    def __init__(self, host='127.0.0.1', port=5555):
        self.host = host
        self.port = port
        self.server_socket = None
        self.clients = {}
        self.lock = threading.Lock()
        self.running = True
    
    def start(self):
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(100)
            
            print(f"🚀 Talkudo Server running on {self.host}:{self.port}")
            print("Press Ctrl+C to stop\n")
            
            while self.running:
                client_socket, address = self.server_socket.accept()
                print(f"📱 New connection from {address}")
                
                client_handler = ClientHandler(client_socket, address, self)
                thread = threading.Thread(target=client_handler.handle)
                thread.daemon = True
                thread.start()
                
        except KeyboardInterrupt:
            print("\n\n👋 Shutting down server...")
        except Exception as e:
            print(f"Server error: {e}")
        finally:
            self.stop()
    
    def add_client(self, user_id, handler):
        with self.lock:
            self.clients[user_id] = handler
            print(f"✅ User {user_id} connected. Total clients: {len(self.clients)}")
    
    def remove_client(self, user_id):
        with self.lock:
            if user_id in self.clients:
                del self.clients[user_id]
                print(f"❌ User {user_id} disconnected. Total clients: {len(self.clients)}")
    
    def get_client(self, user_id):
        with self.lock:
            return self.clients.get(user_id)
    
    def get_all_clients(self):
        with self.lock:
            return self.clients.copy()
    
    def stop(self):
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        print("✅ Server stopped")

if __name__ == "__main__":
    server = ChatServer()
    server.start()