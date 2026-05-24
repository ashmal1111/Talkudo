#!/usr/bin/env python3
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

from server.server import ChatServer

def main():
    print("=" * 50)
    print("🚀 Talkudo Server v1.0.0")
    print("=" * 50)
    print("\nStarting server...")
    
    server = ChatServer(host='127.0.0.1', port=5555)
    
    try:
        server.start()
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down server...")
        server.stop()
        print("✅ Server stopped")

if __name__ == "__main__":
    main()