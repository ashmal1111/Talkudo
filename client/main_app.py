import tkinter as tk
from tkinter import messagebox, scrolledtext, filedialog
import customtkinter as ctk
import socket
import json
import threading
from datetime import datetime
import os
import sys
import random
import string
import re
from PIL import Image, ImageTk
import base64
from io import BytesIO
import time

# Try to import pyaudio for voice messages, but don't fail if not available
try:
    import pyaudio
    import wave
    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False
    print("Note: PyAudio not available - voice messages disabled")

# Set appearance mode
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class LoginWindow:
    def __init__(self, on_login_success):
        self.on_login_success = on_login_success
        self.window = ctk.CTk()
        self.window.title("Talkudo - Login")
        self.window.geometry("400x650")
        self.window.resizable(False, False)
        
        self.setup_ui()
        
    def setup_ui(self):
        self.main_frame = ctk.CTkFrame(self.window, fg_color="transparent")
        self.main_frame.pack(expand=True, fill="both", padx=40, pady=40)
        
        title_label = ctk.CTkLabel(
            self.main_frame,
            text="💬 Talkudo",
            font=ctk.CTkFont(size=36, weight="bold")
        )
        title_label.pack(pady=(0, 10))
        
        subtitle_label = ctk.CTkLabel(
            self.main_frame,
            text="Real-time Messaging Platform",
            font=ctk.CTkFont(size=12)
        )
        subtitle_label.pack(pady=(0, 40))
        
        self.username_entry = ctk.CTkEntry(
            self.main_frame,
            placeholder_text="Username or Email",
            width=280,
            height=45
        )
        self.username_entry.pack(pady=(0, 15))
        self.username_entry.bind('<Return>', lambda e: self.password_entry.focus())
        
        self.password_entry = ctk.CTkEntry(
            self.main_frame,
            placeholder_text="Password",
            show="●",
            width=280,
            height=45
        )
        self.password_entry.pack(pady=(0, 10))
        self.password_entry.bind('<Return>', lambda e: self.login())
        
        self.forgot_password_label = ctk.CTkLabel(
            self.main_frame,
            text="Forgot Password?",
            font=ctk.CTkFont(size=11, underline=True),
            text_color="#7289da",
            cursor="hand2"
        )
        self.forgot_password_label.pack(pady=(0, 15))
        self.forgot_password_label.bind("<Button-1>", lambda e: self.forgot_password())
        
        self.remember_var = tk.BooleanVar()
        remember_check = ctk.CTkCheckBox(
            self.main_frame,
            text="Remember me",
            variable=self.remember_var
        )
        remember_check.pack(pady=(0, 20))
        
        self.login_button = ctk.CTkButton(
            self.main_frame,
            text="Login",
            width=280,
            height=45,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.login
        )
        self.login_button.pack(pady=(0, 15))
        
        self.register_button = ctk.CTkButton(
            self.main_frame,
            text="Create Account",
            width=280,
            height=40,
            fg_color="transparent",
            border_width=2,
            command=self.open_register
        )
        self.register_button.pack()
        
        self.status_label = ctk.CTkLabel(
            self.main_frame,
            text="",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        self.status_label.pack(pady=(10, 0))
        
        self.load_saved_credentials()
    
    def load_saved_credentials(self):
        try:
            if os.path.exists("session.json"):
                with open("session.json", "r") as f:
                    data = json.load(f)
                    if data.get("remember"):
                        self.username_entry.insert(0, data.get("username", ""))
                        self.password_entry.insert(0, data.get("password", ""))
                        self.remember_var.set(True)
        except:
            pass
    
    def save_credentials(self, username, password):
        if self.remember_var.get():
            with open("session.json", "w") as f:
                json.dump({"username": username, "password": password, "remember": True}, f)
    
    def forgot_password(self):
        forgot_window = ctk.CTkToplevel(self.window)
        forgot_window.title("Forgot Password")
        forgot_window.geometry("400x400")
        forgot_window.resizable(False, False)
        forgot_window.transient(self.window)
        forgot_window.grab_set()
        
        main_frame = ctk.CTkFrame(forgot_window, fg_color="transparent")
        main_frame.pack(expand=True, fill="both", padx=40, pady=40)
        
        title_label = ctk.CTkLabel(
            main_frame,
            text="Reset Password",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(0, 20))
        
        info_label = ctk.CTkLabel(
            main_frame,
            text="Enter your email address to receive\na password reset link",
            font=ctk.CTkFont(size=12),
            justify="center"
        )
        info_label.pack(pady=(0, 30))
        
        self.reset_email_entry = ctk.CTkEntry(
            main_frame,
            placeholder_text="Email address",
            width=280,
            height=45
        )
        self.reset_email_entry.pack(pady=(0, 20))
        self.reset_email_entry.bind('<Return>', lambda e: self.send_reset_link(forgot_window))
        
        send_button = ctk.CTkButton(
            main_frame,
            text="Send Reset Link",
            width=280,
            height=40,
            command=lambda: self.send_reset_link(forgot_window)
        )
        send_button.pack(pady=(0, 15))
        
        back_label = ctk.CTkLabel(
            main_frame,
            text="Back to Login",
            font=ctk.CTkFont(size=11, underline=True),
            text_color="#7289da",
            cursor="hand2"
        )
        back_label.pack()
        back_label.bind("<Button-1>", lambda e: forgot_window.destroy())
    
    def send_reset_link(self, window):
        email = self.reset_email_entry.get()
        if not email:
            messagebox.showerror("Error", "Please enter your email address")
            return
        
        reset_token = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
        messagebox.showinfo("Reset Link Sent", f"If an account exists with {email}, you will receive a password reset link.\n\nDemo token: {reset_token}")
        window.destroy()
    
    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Please enter username/email and password")
            return
        
        self.login_button.configure(state="disabled", text="Logging in...")
        self.status_label.configure(text="Connecting to server...", text_color="orange")
        threading.Thread(target=self.authenticate, args=(username, password), daemon=True).start()
    
    def authenticate(self, username, password):
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.settimeout(5)
            client_socket.connect(('127.0.0.1', 5555))
            
            auth_message = {'type': 'auth', 'action': 'login', 'username': username, 'password': password}
            client_socket.send(json.dumps(auth_message).encode('utf-8'))
            
            response = json.loads(client_socket.recv(4096).decode('utf-8'))
            
            if response['status'] == 'success':
                self.save_credentials(username, password)
                user_info = {'user_id': response['user_id'], 'username': response['username'], 'socket': client_socket}
                self.window.after(0, self.login_success, user_info)
            else:
                self.window.after(0, self.login_failed, response.get('message', 'Authentication failed'))
        except socket.timeout:
            self.window.after(0, self.login_failed, "Connection timeout - Server not responding")
        except ConnectionRefusedError:
            self.window.after(0, self.login_failed, "Cannot connect to server - Make sure server is running")
        except Exception as e:
            self.window.after(0, self.login_failed, f"Connection error: {str(e)}")
    
    def login_success(self, user_info):
        self.window.destroy()
        self.on_login_success(user_info)
    
    def login_failed(self, error_message):
        self.login_button.configure(state="normal", text="Login")
        self.status_label.configure(text="")
        messagebox.showerror("Login Failed", error_message)
    
    def open_register(self):
        RegisterWindow(self.window)
    
    def run(self):
        self.window.mainloop()

class RegisterWindow:
    def __init__(self, parent):
        self.parent = parent
        self.window = ctk.CTkToplevel(parent)
        self.window.title("Talkudo - Register")
        self.window.geometry("400x600")
        self.window.resizable(False, False)
        self.setup_ui()
    
    def setup_ui(self):
        main_frame = ctk.CTkFrame(self.window, fg_color="transparent")
        main_frame.pack(expand=True, fill="both", padx=40, pady=40)
        
        title_label = ctk.CTkLabel(main_frame, text="Create Account", font=ctk.CTkFont(size=28, weight="bold"))
        title_label.pack(pady=(0, 30))
        
        self.username_entry = ctk.CTkEntry(main_frame, placeholder_text="Username", width=280, height=45)
        self.username_entry.pack(pady=(0, 15))
        self.username_entry.bind('<Return>', lambda e: self.email_entry.focus())
        
        self.email_entry = ctk.CTkEntry(main_frame, placeholder_text="Email", width=280, height=45)
        self.email_entry.pack(pady=(0, 15))
        self.email_entry.bind('<Return>', lambda e: self.password_entry.focus())
        
        self.password_entry = ctk.CTkEntry(main_frame, placeholder_text="Password", show="●", width=280, height=45)
        self.password_entry.pack(pady=(0, 15))
        self.password_entry.bind('<Return>', lambda e: self.confirm_entry.focus())
        
        self.confirm_entry = ctk.CTkEntry(main_frame, placeholder_text="Confirm Password", show="●", width=280, height=45)
        self.confirm_entry.pack(pady=(0, 20))
        self.confirm_entry.bind('<Return>', lambda e: self.register())
        
        self.register_button = ctk.CTkButton(main_frame, text="Register", width=280, height=45, font=ctk.CTkFont(size=14, weight="bold"), command=self.register)
        self.register_button.pack()
        
        self.status_label = ctk.CTkLabel(main_frame, text="", font=ctk.CTkFont(size=11), text_color="gray")
        self.status_label.pack(pady=(10, 0))
    
    def register(self):
        username = self.username_entry.get()
        email = self.email_entry.get()
        password = self.password_entry.get()
        confirm = self.confirm_entry.get()
        
        if not all([username, email, password, confirm]):
            messagebox.showerror("Error", "Please fill all fields")
            return
        if password != confirm:
            messagebox.showerror("Error", "Passwords do not match")
            return
        if len(password) < 4:
            messagebox.showerror("Error", "Password must be at least 4 characters")
            return
        
        self.register_button.configure(state="disabled", text="Registering...")
        self.status_label.configure(text="Connecting to server...", text_color="orange")
        threading.Thread(target=self.do_register, args=(username, email, password), daemon=True).start()
    
    def do_register(self, username, email, password):
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.settimeout(5)
            client_socket.connect(('127.0.0.1', 5555))
            
            register_message = {'type': 'auth', 'action': 'register', 'username': username, 'email': email, 'password': password}
            client_socket.send(json.dumps(register_message).encode('utf-8'))
            
            response = json.loads(client_socket.recv(4096).decode('utf-8'))
            client_socket.close()
            
            if response['status'] == 'success':
                self.window.after(0, self.register_success)
            else:
                self.window.after(0, self.register_failed, response['message'])
        except Exception as e:
            self.window.after(0, self.register_failed, f"Connection error: {str(e)}")
    
    def register_success(self):
        self.status_label.configure(text="")
        messagebox.showinfo("Success", "Registration successful! Please login.")
        self.window.destroy()
    
    def register_failed(self, error):
        self.register_button.configure(state="normal", text="Register")
        self.status_label.configure(text="")
        messagebox.showerror("Registration Failed", error)

class Message:
    def __init__(self, message_id, sender_id, sender_name, content, timestamp, is_own=False, reply_to=None, reactions=None):
        self.message_id = message_id
        self.sender_id = sender_id
        self.sender_name = sender_name
        self.content = content
        self.timestamp = timestamp
        self.is_own = is_own
        self.reply_to = reply_to
        self.reactions = reactions or {}
        self.edited = False
        self.deleted = False

class ChatInterface:
    def __init__(self, user_info):
        self.user_info = user_info
        self.socket = user_info['socket']
        self.current_chat = None
        self.current_chat_name = None
        self.messages = {}
        self.users = {}
        self.replying_to = None
        self.editing_message = None
        self.voice_recording = False
        self.audio_frames = []
        self.receiver_running = True
        self.reconnect_attempts = 0
        
        # Custom status
        self.custom_status = "Available"
        
        self.setup_ui()
        threading.Thread(target=self.receive_messages, daemon=True).start()
        self.request_user_list()
    
    def setup_ui(self):
        self.window = ctk.CTk()
        self.window.title(f"Talkudo - {self.user_info['username']}")
        self.window.geometry("1200x700")
        
        self.window.grid_columnconfigure(0, weight=0)
        self.window.grid_columnconfigure(1, weight=1)
        self.window.grid_rowconfigure(0, weight=1)
        
        self.setup_sidebar()
        self.setup_chat_area()
        
        self.window.bind('<Return>', self.on_enter_key)
        self.window.bind('<Control-Return>', self.on_ctrl_enter)
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_sidebar(self):
        self.sidebar = ctk.CTkFrame(self.window, width=280, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        
        # User info with custom status
        self.user_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.user_frame.pack(fill="x", padx=15, pady=15)
        
        user_label = ctk.CTkLabel(self.user_frame, text="👤", font=ctk.CTkFont(size=40))
        user_label.pack(side="left", padx=(0, 10))
        
        user_details = ctk.CTkFrame(self.user_frame, fg_color="transparent")
        user_details.pack(side="left", fill="both", expand=True)
        
        self.username_label = ctk.CTkLabel(user_details, text=self.user_info['username'], font=ctk.CTkFont(size=16, weight="bold"), anchor="w")
        self.username_label.pack(fill="x")
        
        # Custom status with edit button
        status_frame = ctk.CTkFrame(user_details, fg_color="transparent")
        status_frame.pack(fill="x")
        
        self.status_label = ctk.CTkLabel(status_frame, text=f"● {self.custom_status}", font=ctk.CTkFont(size=11), text_color="#3ba55d", anchor="w")
        self.status_label.pack(side="left")
        
        edit_status_btn = ctk.CTkButton(status_frame, text="✏️", width=25, height=20, command=self.edit_custom_status)
        edit_status_btn.pack(side="left", padx=(5, 0))
        
        # Connection status
        self.conn_status_label = ctk.CTkLabel(user_details, text="● Connected", font=ctk.CTkFont(size=10), text_color="#3ba55d", anchor="w")
        self.conn_status_label.pack(fill="x")
        
        self.search_entry = ctk.CTkEntry(self.sidebar, placeholder_text="Search users...", height=35)
        self.search_entry.pack(fill="x", padx=15, pady=(0, 15))
        self.search_entry.bind('<KeyRelease>', self.search_users)
        
        self.users_label = ctk.CTkLabel(self.sidebar, text="CONTACTS", font=ctk.CTkFont(size=11, weight="bold"), text_color="gray")
        self.users_label.pack(anchor="w", padx=15, pady=(0, 5))
        
        self.users_frame = ctk.CTkScrollableFrame(self.sidebar, fg_color="transparent")
        self.users_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Quick actions buttons
        actions_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        actions_frame.pack(fill="x", padx=15, pady=(0, 10))
        
        shortcuts_btn = ctk.CTkButton(actions_frame, text="⌨️ Shortcuts", width=120, command=self.show_shortcuts)
        shortcuts_btn.pack(side="left", padx=(0, 5))
        
        stats_btn = ctk.CTkButton(actions_frame, text="📊 Stats", width=120, command=self.show_stats)
        stats_btn.pack(side="right")
        
        self.logout_button = ctk.CTkButton(self.sidebar, text="Logout", height=35, fg_color="#ed4245", hover_color="#c03537", command=self.logout)
        self.logout_button.pack(fill="x", padx=15, pady=15)
    
    def setup_chat_area(self):
        self.chat_area = ctk.CTkFrame(self.window, corner_radius=0)
        self.chat_area.grid(row=0, column=1, sticky="nsew")
        
        self.chat_header = ctk.CTkFrame(self.chat_area, height=60, corner_radius=0)
        self.chat_header.pack(fill="x", side="top")
        self.chat_header.pack_propagate(False)
        
        self.chat_title = ctk.CTkLabel(self.chat_header, text="Select a contact to start messaging", font=ctk.CTkFont(size=18, weight="bold"))
        self.chat_title.pack(side="left", padx=20, pady=10)
        
        # Chat actions
        chat_actions = ctk.CTkFrame(self.chat_header, fg_color="transparent")
        chat_actions.pack(side="right", padx=20)
        
        self.search_chat_btn = ctk.CTkButton(chat_actions, text="🔍", width=40, command=self.search_in_chat)
        self.search_chat_btn.pack(side="left", padx=5)
        
        self.theme_button = ctk.CTkButton(chat_actions, text="🌙", width=40, command=self.toggle_theme)
        self.theme_button.pack(side="left", padx=5)
        
        self.reconnect_btn = ctk.CTkButton(chat_actions, text="🔄", width=40, command=self.manual_reconnect, fg_color="#ed4245")
        self.reconnect_btn.pack(side="left", padx=5)
        
        self.reply_indicator = ctk.CTkFrame(self.chat_area, fg_color="#4e5d94", height=40, corner_radius=5)
        self.reply_indicator.pack(fill="x", padx=20, pady=(5, 0))
        self.reply_indicator.pack_forget()
        
        self.messages_frame = ctk.CTkScrollableFrame(self.chat_area, fg_color="transparent")
        self.messages_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.typing_label = ctk.CTkLabel(self.chat_area, text="", font=ctk.CTkFont(size=11), text_color="gray")
        self.typing_label.pack(anchor="w", padx=20, pady=(0, 5))
        
        input_frame = ctk.CTkFrame(self.chat_area, fg_color="transparent")
        input_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        self.message_input = ctk.CTkTextbox(input_frame, height=80, font=ctk.CTkFont(size=13))
        self.message_input.pack(side="left", fill="both", expand=True, padx=(0, 10))
        self.message_input.bind('<KeyRelease>', self.on_typing)
        
        hint_label = ctk.CTkLabel(input_frame, text="Press Enter to send • Ctrl+Enter for new line • Markdown supported", font=ctk.CTkFont(size=10), text_color="gray")
        hint_label.pack(side="bottom", pady=(5, 0))
        
        buttons_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        buttons_frame.pack(side="right")
        
        self.emoji_button = ctk.CTkButton(buttons_frame, text="😊", width=40, command=self.open_emoji_picker)
        self.emoji_button.pack(pady=(0, 5))
        
        self.attach_button = ctk.CTkButton(buttons_frame, text="📎", width=40, command=self.attach_file)
        self.attach_button.pack(pady=(0, 5))
        
        if PYAUDIO_AVAILABLE:
            self.voice_button = ctk.CTkButton(buttons_frame, text="🎤", width=40, command=self.toggle_voice_recording)
            self.voice_button.pack(pady=(0, 5))
        
        self.send_button = ctk.CTkButton(buttons_frame, text="Send", width=60, command=self.send_message)
        self.send_button.pack()
    
    def manual_reconnect(self):
        """Manually reconnect to server"""
        self.reconnect_btn.configure(state="disabled", text="🔄 Connecting...")
        threading.Thread(target=self.reconnect_to_server, daemon=True).start()
    
    def reconnect_to_server(self):
        """Attempt to reconnect to the server"""
        try:
            # Close old socket if exists
            try:
                self.socket.close()
            except:
                pass
            
            # Create new connection
            new_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            new_socket.settimeout(5)
            new_socket.connect(('127.0.0.1', 5555))
            
            # Re-authenticate
            auth_message = {'type': 'auth', 'action': 'login', 'username': self.user_info['username'], 'password': self.user_info.get('password', '')}
            new_socket.send(json.dumps(auth_message).encode('utf-8'))
            
            response = json.loads(new_socket.recv(4096).decode('utf-8'))
            
            if response['status'] == 'success':
                self.socket = new_socket
                self.user_info['socket'] = new_socket
                self.receiver_running = False
                time.sleep(1)
                self.receiver_running = True
                threading.Thread(target=self.receive_messages, daemon=True).start()
                self.request_user_list()
                
                self.window.after(0, self.reconnect_success)
            else:
                self.window.after(0, self.reconnect_failed, "Authentication failed")
        except Exception as e:
            self.window.after(0, self.reconnect_failed, str(e))
    
    def reconnect_success(self):
        """Handle successful reconnection"""
        self.conn_status_label.configure(text="● Connected", text_color="#3ba55d")
        self.reconnect_btn.configure(state="normal", text="🔄", fg_color="#ed4245")
        messagebox.showinfo("Reconnected", "Successfully reconnected to server!")
    
    def reconnect_failed(self, error):
        """Handle failed reconnection"""
        self.conn_status_label.configure(text="● Disconnected", text_color="red")
        self.reconnect_btn.configure(state="normal", text="🔄", fg_color="#ed4245")
        
        retry = messagebox.askretrycancel("Connection Lost", f"Failed to reconnect: {error}\nWould you like to retry?")
        if retry:
            self.manual_reconnect()
    
    def edit_custom_status(self):
        dialog = ctk.CTkToplevel(self.window)
        dialog.title("Set Custom Status")
        dialog.geometry("300x200")
        
        label = ctk.CTkLabel(dialog, text="Set your status:", font=ctk.CTkFont(size=14))
        label.pack(pady=10)
        
        status_entry = ctk.CTkEntry(dialog, placeholder_text="e.g., Working, Gaming, Away", width=250)
        status_entry.pack(pady=10)
        status_entry.insert(0, self.custom_status)
        
        def save_status():
            new_status = status_entry.get()
            if new_status:
                self.custom_status = new_status
                self.status_label.configure(text=f"● {self.custom_status}")
                dialog.destroy()
        
        save_btn = ctk.CTkButton(dialog, text="Save", command=save_status)
        save_btn.pack(pady=10)
    
    def show_shortcuts(self):
        shortcuts_text = """
📌 Keyboard Shortcuts:

General:
• Ctrl + N - New Chat
• Ctrl + F - Search
• Ctrl + S - Settings
• Ctrl + Q - Quit

Chat:
• Enter - Send Message
• Ctrl + Enter - New Line
• Ctrl + E - Emoji Picker
• Ctrl + Up - Edit Last Message
• Ctrl + D - Delete Message
• Ctrl + R - Reply to Message
• Ctrl + P - Pin Message

Navigation:
• Ctrl + Tab - Next Chat
• Ctrl + Shift + Tab - Previous Chat
• Esc - Cancel Reply/Edit
        """
        messagebox.showinfo("Keyboard Shortcuts", shortcuts_text)
    
    def show_stats(self):
        total_messages = len([m for m in self.messages.values() if m.sender_id == self.user_info['user_id']])
        received_messages = len([m for m in self.messages.values() if m.sender_id != self.user_info['user_id']])
        
        stats_text = f"""
📊 Your Chat Statistics:

Total Messages Sent: {total_messages}
Total Messages Received: {received_messages}
Total Conversations: {len(self.users)}
Active Contacts: {len([u for u in self.users.values() if u.get('status') == 'online'])}
Custom Status: {self.custom_status}
        """
        messagebox.showinfo("Statistics", stats_text)
    
    def search_in_chat(self):
        if not self.current_chat:
            return
        
        search_window = ctk.CTkToplevel(self.window)
        search_window.title("Search in Chat")
        search_window.geometry("500x600")
        
        search_entry = ctk.CTkEntry(search_window, placeholder_text="Search messages...")
        search_entry.pack(fill="x", padx=20, pady=20)
        
        results_frame = ctk.CTkScrollableFrame(search_window, fg_color="transparent")
        results_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        def perform_search():
            query = search_entry.get().lower()
            for widget in results_frame.winfo_children():
                widget.destroy()
            
            found = 0
            for msg_id, msg in self.messages.items():
                if query in msg.content.lower():
                    found += 1
                    result_frame = ctk.CTkFrame(results_frame, fg_color="#4e5d94", corner_radius=5)
                    result_frame.pack(fill="x", pady=5)
                    
                    sender_label = ctk.CTkLabel(result_frame, text=f"{msg.sender_name}:", font=ctk.CTkFont(weight="bold"))
                    sender_label.pack(anchor="w", padx=10, pady=(5, 0))
                    
                    content_label = ctk.CTkLabel(result_frame, text=msg.content[:100], wraplength=400, justify="left")
                    content_label.pack(anchor="w", padx=10, pady=5)
                    
                    time_label = ctk.CTkLabel(result_frame, text=msg.timestamp.strftime("%Y-%m-%d %H:%M"), font=ctk.CTkFont(size=10), text_color="gray")
                    time_label.pack(anchor="e", padx=10, pady=(0, 5))
            
            if found == 0:
                no_results = ctk.CTkLabel(results_frame, text="No messages found")
                no_results.pack(pady=20)
        
        search_button = ctk.CTkButton(search_window, text="Search", command=perform_search)
        search_button.pack(pady=(0, 20))
    
    def attach_file(self):
        if not self.current_chat:
            messagebox.showwarning("No Chat", "Please select a chat first")
            return
        
        file_path = filedialog.askopenfilename()
        if file_path:
            threading.Thread(target=self.send_file, args=(file_path,), daemon=True).start()
    
    def send_file(self, file_path):
        try:
            with open(file_path, 'rb') as f:
                file_data = base64.b64encode(f.read()).decode('utf-8')
            
            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)
            
            message = {
                'type': 'message',
                'receiver_id': self.current_chat,
                'content': f"📎 {file_name} ({file_size} bytes)",
                'message_type': 'file',
                'file_data': file_data,
                'file_name': file_name
            }
            self.socket.send(json.dumps(message).encode('utf-8'))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send file: {e}")
    
    def toggle_voice_recording(self):
        if not PYAUDIO_AVAILABLE:
            messagebox.showinfo("Info", "Voice messages require PyAudio. Install with: pip install pyaudio")
            return
        
        if not self.current_chat:
            messagebox.showwarning("No Chat", "Please select a chat first")
            return
        
        if not self.voice_recording:
            self.start_recording()
        else:
            self.stop_recording()
    
    def start_recording(self):
        self.voice_recording = True
        self.voice_button.configure(fg_color="red", text="🔴")
        self.audio_frames = []
        
        def record():
            CHUNK = 1024
            FORMAT = pyaudio.paInt16
            CHANNELS = 1
            RATE = 44100
            
            p = pyaudio.PyAudio()
            stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
            
            for _ in range(0, int(RATE / CHUNK * 5)):  # Record 5 seconds
                if not self.voice_recording:
                    break
                data = stream.read(CHUNK)
                self.audio_frames.append(data)
            
            stream.stop_stream()
            stream.close()
            p.terminate()
        
        threading.Thread(target=record, daemon=True).start()
    
    def stop_recording(self):
        self.voice_recording = False
        self.voice_button.configure(fg_color="transparent", text="🎤")
        
        if self.audio_frames:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"voice_{timestamp}.wav"
            
            wf = wave.open(filename, 'wb')
            wf.setnchannels(1)
            wf.setsampwidth(pyaudio.PyAudio().get_sample_size(pyaudio.paInt16))
            wf.setframerate(44100)
            wf.writeframes(b''.join(self.audio_frames))
            wf.close()
            
            self.send_file(filename)
            os.remove(filename)
    
    def receive_messages(self):
        while self.receiver_running:
            try:
                self.socket.settimeout(1)
                data = self.socket.recv(4096).decode('utf-8')
                if not data:
                    break
                
                message = json.loads(data)
                self.window.after(0, self.handle_received_message, message)
            except socket.timeout:
                continue
            except Exception as e:
                if self.receiver_running:
                    print(f"Receive error: {e}")
                    self.window.after(0, self.connection_lost)
                break
    
    def connection_lost(self):
        """Handle lost connection"""
        self.conn_status_label.configure(text="● Disconnected", text_color="red")
        self.reconnect_btn.configure(fg_color="#3ba55d")
        
        result = messagebox.askretrycancel("Connection Lost", "Connection to server lost. Would you like to reconnect?")
        if result:
            self.manual_reconnect()
    
    def handle_received_message(self, message):
        msg_type = message.get('type')
        
        if msg_type == 'message':
            self.play_notification()
            msg = Message(
                message.get('message_id', random.randint(1, 10000)),
                message['sender_id'],
                message['sender_name'],
                message['content'],
                datetime.fromisoformat(message['timestamp']) if isinstance(message['timestamp'], str) else datetime.now(),
                False,
                message.get('reply_to')
            )
            self.messages[msg.message_id] = msg
            
            if message['sender_id'] == self.current_chat:
                self.display_message(msg)
        
        elif msg_type == 'user_list':
            self.update_users_list(message['users'])
        
        elif msg_type == 'message_history':
            for msg_data in message['messages']:
                msg = Message(
                    msg_data['message_id'],
                    msg_data['sender_id'],
                    msg_data['sender_name'],
                    msg_data['content'],
                    datetime.fromisoformat(msg_data['timestamp']) if isinstance(msg_data['timestamp'], str) else datetime.now(),
                    msg_data['sender_id'] == self.user_info['user_id']
                )
                self.messages[msg.message_id] = msg
                self.display_message(msg)
        
        elif msg_type == 'typing':
            if message['user_id'] == self.current_chat:
                self.typing_label.configure(text=f"{message['username']} is typing..." if message['is_typing'] else "")
        
        elif msg_type == 'status_update':
            self.update_user_status(message['user_id'], message['status'])
        
        elif msg_type == 'reaction':
            self.handle_reaction(message)
        
        elif msg_type == 'message_deleted':
            if message['message_id'] in self.messages:
                self.messages[message['message_id']].deleted = True
                self.refresh_chat()
        
        elif msg_type == 'message_edited':
            if message['message_id'] in self.messages:
                self.messages[message['message_id']].content = message['new_content']
                self.messages[message['message_id']].edited = True
                self.refresh_chat()
    
    def handle_reaction(self, reaction_data):
        message_id = reaction_data['message_id']
        emoji = reaction_data['emoji']
        user_id = reaction_data['user_id']
        
        if message_id in self.messages:
            if emoji not in self.messages[message_id].reactions:
                self.messages[message_id].reactions[emoji] = set()
            if user_id in self.messages[message_id].reactions[emoji]:
                self.messages[message_id].reactions[emoji].remove(user_id)
                if not self.messages[message_id].reactions[emoji]:
                    del self.messages[message_id].reactions[emoji]
            else:
                self.messages[message_id].reactions[emoji].add(user_id)
            self.refresh_chat()
    
    def refresh_chat(self):
        if self.current_chat:
            for widget in self.messages_frame.winfo_children():
                widget.destroy()
            for msg in self.messages.values():
                if msg.sender_id == self.current_chat or msg.sender_id == self.user_info['user_id']:
                    self.display_message(msg)
    
    def display_message(self, message):
        msg_frame = ctk.CTkFrame(self.messages_frame, fg_color="transparent")
        msg_frame.pack(fill="x", pady=(5, 5))
        
        def show_context_menu(event):
            menu = tk.Menu(self.window, tearoff=0)
            menu.add_command(label="📋 Copy Text", command=lambda: self.copy_message(message))
            menu.add_command(label="↩️ Reply", command=lambda: self.start_reply(message))
            menu.add_command(label="❤️ React", command=lambda: self.show_reaction_picker(message))
            menu.add_separator()
            if message.is_own:
                menu.add_command(label="✏️ Edit", command=lambda: self.edit_message(message))
                menu.add_command(label="🗑️ Delete for Everyone", command=lambda: self.delete_message(message))
            menu.add_command(label="📌 Pin", command=lambda: self.pin_message(message))
            menu.add_command(label="↗️ Forward", command=lambda: self.forward_message(message))
            menu.post(event.x_root, event.y_root)
        
        if message.is_own:
            container = ctk.CTkFrame(msg_frame, fg_color="#7289da", corner_radius=10)
            container.pack(side="right", padx=10, pady=2)
        else:
            container = ctk.CTkFrame(msg_frame, fg_color="#4e5d94", corner_radius=10)
            container.pack(side="left", padx=10, pady=2)
        
        container.bind("<Button-3>", show_context_menu)
        
        # Reply indicator
        if message.reply_to and message.reply_to in self.messages:
            reply_msg = self.messages[message.reply_to]
            reply_frame = ctk.CTkFrame(container, fg_color="#3a4a7a", corner_radius=5)
            reply_frame.pack(fill="x", padx=10, pady=(5, 0))
            
            reply_label = ctk.CTkLabel(reply_frame, text=f"↩️ Replying to {reply_msg.sender_name}", font=ctk.CTkFont(size=10), text_color="#a0a0a0")
            reply_label.pack(anchor="w", padx=5, pady=(2, 0))
            
            reply_content = ctk.CTkLabel(reply_frame, text=reply_msg.content[:100], font=ctk.CTkFont(size=11), text_color="#c0c0c0", wraplength=350, justify="left")
            reply_content.pack(anchor="w", padx=5, pady=(0, 2))
        
        if not message.is_own:
            name_label = ctk.CTkLabel(container, text=message.sender_name, font=ctk.CTkFont(size=11, weight="bold"), text_color="#ffffff")
            name_label.pack(anchor="w", padx=10, pady=(5, 0))
        
        content_text = message.content if not message.deleted else "[Message Deleted]"
        content_label = ctk.CTkLabel(container, text=content_text, font=ctk.CTkFont(size=13), text_color="#ffffff" if not message.deleted else "#a0a0a0", wraplength=400, justify="left")
        content_label.pack(anchor="w", padx=10, pady=5)
        
        if message.edited:
            edited_label = ctk.CTkLabel(container, text="(edited)", font=ctk.CTkFont(size=9), text_color="#d3d3d3")
            edited_label.pack(anchor="e", padx=10)
        
        if message.reactions:
            reactions_frame = ctk.CTkFrame(container, fg_color="transparent")
            reactions_frame.pack(anchor="w", padx=10, pady=(0, 5))
            
            for emoji, users in message.reactions.items():
                react_btn = ctk.CTkButton(
                    reactions_frame,
                    text=f"{emoji} {len(users)}",
                    width=50,
                    height=25,
                    font=ctk.CTkFont(size=11),
                    command=lambda e=emoji, m=message: self.toggle_reaction(m, e)
                )
                react_btn.pack(side="left", padx=2)
        
        time_str = message.timestamp.strftime("%H:%M")
        time_label = ctk.CTkLabel(container, text=time_str, font=ctk.CTkFont(size=9), text_color="#d3d3d3")
        time_label.pack(anchor="e", padx=10, pady=(0, 5))
        
        self.messages_frame._parent_canvas.yview_moveto(1)
    
    def copy_message(self, message):
        self.window.clipboard_clear()
        self.window.clipboard_append(message.content)
    
    def start_reply(self, message):
        self.replying_to = message
        self.reply_indicator.pack(fill="x", padx=20, pady=(5, 0))
        
        for widget in self.reply_indicator.winfo_children():
            widget.destroy()
        
        reply_text = ctk.CTkLabel(self.reply_indicator, text=f"Replying to {message.sender_name}: {message.content[:50]}", font=ctk.CTkFont(size=11))
        reply_text.pack(side="left", padx=10, pady=5)
        
        cancel_btn = ctk.CTkButton(self.reply_indicator, text="Cancel", width=60, height=25, command=self.cancel_reply)
        cancel_btn.pack(side="right", padx=10)
    
    def cancel_reply(self):
        self.replying_to = None
        self.reply_indicator.pack_forget()
    
    def show_reaction_picker(self, message):
        reaction_window = ctk.CTkToplevel(self.window)
        reaction_window.title("Add Reaction")
        reaction_window.geometry("400x100")
        
        emojis = ["❤️", "👍", "😂", "😮", "😢", "😡", "🎉", "⭐"]
        
        for i, emoji in enumerate(emojis):
            btn = ctk.CTkButton(
                reaction_window,
                text=emoji,
                width=50,
                height=50,
                font=ctk.CTkFont(size=24),
                command=lambda e=emoji: self.toggle_reaction(message, e, reaction_window)
            )
            btn.grid(row=0, column=i, padx=5, pady=10)
    
    def toggle_reaction(self, message, emoji, window=None):
        reaction_msg = {
            'type': 'reaction',
            'message_id': message.message_id,
            'emoji': emoji,
            'user_id': self.user_info['user_id']
        }
        try:
            self.socket.send(json.dumps(reaction_msg).encode('utf-8'))
        except:
            pass
        if window:
            window.destroy()
    
    def edit_message(self, message):
        self.editing_message = message
        self.message_input.delete("1.0", "end")
        self.message_input.insert("1.0", message.content)
        
        self.send_button.configure(text="Update", command=lambda: self.update_message(message))
    
    def update_message(self, message):
        new_content = self.message_input.get("1.0", "end-1c").strip()
        if new_content:
            edit_msg = {
                'type': 'edit_message',
                'message_id': message.message_id,
                'new_content': new_content
            }
            try:
                self.socket.send(json.dumps(edit_msg).encode('utf-8'))
                message.content = new_content
                message.edited = True
                self.refresh_chat()
            except:
                messagebox.showerror("Error", "Failed to edit message - Connection lost")
        
        self.editing_message = None
        self.send_button.configure(text="Send", command=self.send_message)
        self.message_input.delete("1.0", "end")
    
    def delete_message(self, message):
        if messagebox.askyesno("Delete Message", "Delete this message for everyone?"):
            delete_msg = {
                'type': 'delete_message',
                'message_id': message.message_id
            }
            try:
                self.socket.send(json.dumps(delete_msg).encode('utf-8'))
                message.deleted = True
                self.refresh_chat()
            except:
                messagebox.showerror("Error", "Failed to delete message - Connection lost")
    
    def pin_message(self, message):
        messagebox.showinfo("Pinned", f"Pinned message: {message.content[:100]}")
    
    def forward_message(self, message):
        forward_window = ctk.CTkToplevel(self.window)
        forward_window.title("Forward Message")
        forward_window.geometry("300x400")
        
        label = ctk.CTkLabel(forward_window, text="Select contact:", font=ctk.CTkFont(size=14))
        label.pack(pady=10)
        
        contacts_frame = ctk.CTkScrollableFrame(forward_window, fg_color="transparent")
        contacts_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        for user_id, user_info in self.users.items():
            btn = ctk.CTkButton(
                contacts_frame,
                text=user_info.get('username', 'Unknown'),
                command=lambda uid=user_id: self.forward_to_contact(message, uid, forward_window)
            )
            btn.pack(fill="x", pady=2)
    
    def forward_to_contact(self, message, contact_id, window):
        forward_msg = {
            'type': 'message',
            'receiver_id': contact_id,
            'content': f"Forwarded from {message.sender_name}: {message.content}",
            'message_type': 'text'
        }
        try:
            self.socket.send(json.dumps(forward_msg).encode('utf-8'))
            window.destroy()
            messagebox.showinfo("Forwarded", "Message forwarded successfully!")
        except:
            messagebox.showerror("Error", "Failed to forward - Connection lost")
    
    def send_message(self):
        if not self.current_chat:
            messagebox.showwarning("No Chat", "Please select a chat first")
            return
        
        content = self.message_input.get("1.0", "end-1c").strip()
        if not content:
            return
        
        # Check if AI assistant is mentioned
        if "@ai" in content.lower() or "ai assistant" in content.lower():
            self.get_ai_response(content)
            return
        
        message = {
            'type': 'message',
            'receiver_id': self.current_chat,
            'content': content,
            'message_type': 'text',
            'reply_to': self.replying_to.message_id if self.replying_to else None
        }
        
        try:
            self.socket.send(json.dumps(message).encode('utf-8'))
            self.message_input.delete("1.0", "end")
            self.cancel_reply()
            
            own_message = Message(
                random.randint(10000, 99999),
                self.user_info['user_id'],
                self.user_info['username'],
                content,
                datetime.now(),
                True,
                self.replying_to.message_id if self.replying_to else None
            )
            self.messages[own_message.message_id] = own_message
            self.display_message(own_message)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send message: {str(e)}")
    
    def get_ai_response(self, user_message):
        ai_responses = {
            "hello": "Hello! How can I help you today?",
            "hi": "Hi there! 👋",
            "how are you": "I'm doing great, thanks for asking! 😊",
            "help": "I can help with:\n- Answering questions\n- Setting reminders\n- Providing information\n- Chatting with you!",
            "joke": "Why don't programmers like nature? It has too many bugs! 😄",
            "time": f"The current time is {datetime.now().strftime('%H:%M:%S')}",
            "thanks": "You're welcome! Happy to help! 🎉"
        }
        
        response = "I'm your AI assistant! I can help with basic questions. Try asking me for a joke or greeting!"
        for key, value in ai_responses.items():
            if key in user_message.lower():
                response = value
                break
        
        ai_message = {
            'type': 'message',
            'receiver_id': self.current_chat,
            'content': f"🤖 AI Assistant: {response}",
            'message_type': 'text'
        }
        
        try:
            self.socket.send(json.dumps(ai_message).encode('utf-8'))
        except:
            pass
    
    def on_enter_key(self, event):
        if self.message_input.winfo_exists() and self.message_input == self.window.focus_get():
            self.send_message()
            return "break"
    
    def on_ctrl_enter(self, event):
        if self.message_input.winfo_exists():
            self.message_input.insert("end", "\n")
            return "break"
    
    def update_users_list(self, users):
        for widget in self.users_frame.winfo_children():
            widget.destroy()
        
        self.users = {}
        users.sort(key=lambda x: x['status'] != 'online')
        
        for user in users:
            self.add_user_to_list(user)
    
    def add_user_to_list(self, user):
        item_frame = ctk.CTkFrame(self.users_frame, fg_color="transparent")
        item_frame.pack(fill="x", pady=2)
        
        def on_click(e=None):
            self.open_chat(user['user_id'], user['username'])
        
        item_frame.bind("<Button-1>", on_click)
        
        status_color = "#3ba55d" if user['status'] == 'online' else "#808080"
        status_dot = ctk.CTkLabel(item_frame, text="●", font=ctk.CTkFont(size=14), text_color=status_color)
        status_dot.pack(side="left", padx=(5, 5))
        status_dot.bind("<Button-1>", on_click)
        
        avatar = ctk.CTkLabel(item_frame, text="👤", font=ctk.CTkFont(size=20))
        avatar.pack(side="left", padx=(0, 10))
        avatar.bind("<Button-1>", on_click)
        
        name_label = ctk.CTkLabel(item_frame, text=user['username'], font=ctk.CTkFont(size=13), anchor="w")
        name_label.pack(side="left", fill="x", expand=True)
        name_label.bind("<Button-1>", on_click)
        
        self.users[user['user_id']] = {'widget': item_frame, 'username': user['username'], 'status': user['status']}
    
    def open_chat(self, user_id, username):
        self.current_chat = user_id
        self.current_chat_name = username
        self.chat_title.configure(text=username)
        
        for widget in self.messages_frame.winfo_children():
            widget.destroy()
        
        self.messages = {}
        self.load_message_history(user_id)
    
    def load_message_history(self, user_id):
        request = {'type': 'get_history', 'other_user_id': user_id}
        try:
            self.socket.send(json.dumps(request).encode('utf-8'))
        except Exception as e:
            print(f"Load history error: {e}")
    
    def on_typing(self, event):
        if self.current_chat:
            typing_msg = {'type': 'typing', 'receiver_id': self.current_chat, 'is_typing': True}
            try:
                self.socket.send(json.dumps(typing_msg).encode('utf-8'))
            except:
                pass
            
            if hasattr(self, 'typing_timer'):
                self.window.after_cancel(self.typing_timer)
            self.typing_timer = self.window.after(2000, self.stop_typing)
    
    def stop_typing(self):
        if self.current_chat:
            typing_msg = {'type': 'typing', 'receiver_id': self.current_chat, 'is_typing': False}
            try:
                self.socket.send(json.dumps(typing_msg).encode('utf-8'))
            except:
                pass
    
    def request_user_list(self):
        request = {'type': 'get_users'}
        try:
            self.socket.send(json.dumps(request).encode('utf-8'))
        except:
            pass
    
    def search_users(self, event):
        search_text = self.search_entry.get().lower()
        for user_id, user_info in self.users.items():
            if search_text in user_info['username'].lower():
                user_info['widget'].pack(fill="x", pady=2)
            else:
                user_info['widget'].pack_forget()
    
    def update_user_status(self, user_id, status):
        if user_id in self.users:
            self.users[user_id]['status'] = status
            status_dot = self.users[user_id]['widget'].winfo_children()[0]
            status_dot.configure(text_color="#3ba55d" if status == 'online' else "#808080")
    
    def open_emoji_picker(self):
        emoji_window = ctk.CTkToplevel(self.window)
        emoji_window.title("Emojis")
        emoji_window.geometry("400x300")
        
        emojis = ["😀", "😁", "😂", "😃", "😄", "😅", "😆", "😉", "😊", "😋", "😎", "😍", "😘", "🥰", "😗", "😙", "😚", "🙂", "🤗", "🤩", "🤔", "🤨", "😐", "😑", "😶", "🙄", "😏", "😣", "😥", "😮", "🤐", "😯", "😪", "😫", "😴", "😌", "😛", "😜", "😝", "🤤", "😒", "😓", "😔", "😕", "🙃", "🤑", "😲", "☹️", "🙁", "😖", "😞", "😟", "😤", "😢", "😭", "😦", "😧", "😨", "😩", "😰", "😱", "😳", "😵", "😡", "😠"]
        
        emoji_frame = ctk.CTkScrollableFrame(emoji_window, fg_color="transparent")
        emoji_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        for i, emoji_char in enumerate(emojis):
            btn = ctk.CTkButton(emoji_frame, text=emoji_char, width=40, height=40, font=ctk.CTkFont(size=20), command=lambda e=emoji_char: self.insert_emoji(e, emoji_window))
            btn.grid(row=i//8, column=i%8, padx=2, pady=2)
    
    def insert_emoji(self, emoji_char, emoji_window):
        self.message_input.insert("end", emoji_char)
        emoji_window.destroy()
    
    def toggle_theme(self):
        current = ctk.get_appearance_mode()
        new_theme = "Light" if current == "Dark" else "Dark"
        ctk.set_appearance_mode(new_theme)
        self.theme_button.configure(text="☀️" if new_theme == "Light" else "🌙")
    
    def play_notification(self):
        try:
            print('\a', end='', flush=True)
        except:
            pass
    
    def logout(self):
        self.receiver_running = False
        try:
            self.socket.close()
        except:
            pass
        self.window.destroy()
        app = TalkudoApp()
        app.start()
    
    def on_closing(self):
        self.receiver_running = False
        try:
            self.socket.close()
        except:
            pass
        self.window.destroy()
    
    def run(self):
        self.window.mainloop()

class TalkudoApp:
    def __init__(self):
        self.user_info = None
    
    def start(self):
        login = LoginWindow(self.on_login_success)
        login.run()
    
    def on_login_success(self, user_info):
        self.user_info = user_info
        chat_interface = ChatInterface(user_info)
        chat_interface.run()

if __name__ == "__main__":
    app = TalkudoApp()
    app.start()
