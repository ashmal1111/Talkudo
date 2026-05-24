#!/usr/bin/env python3
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

from client.main_app import TalkudoApp

def main():
    print("=" * 50)
    print("💬 Talkudo Client v1.0.0")
    print("=" * 50)
    
    app = TalkudoApp()
    app.start()

if __name__ == "__main__":
    main()