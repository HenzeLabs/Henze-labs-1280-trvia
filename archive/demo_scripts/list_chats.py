#!/usr/bin/env python3
"""
List all available chat names in the iMessage database.
"""

import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_path = Path(__file__).parent / 'backend'
sys.path.insert(0, str(backend_path))

from app.parsers.imessage_parser import iMessageParser
from app.config import Config

def list_all_chats():
    """List all chat names in the database."""
    
    print("📱 Available chats in your iMessage database:")
    print("=" * 50)
    
    try:
        parser = iMessageParser(str(Config.IMESSAGE_DB_PATH), Config.CONTACT_MAP)
        chats = parser.get_all_chat_names()
        
        # Filter out phone numbers and show only named group chats
        group_chats = []
        for chat in chats:
            if chat and not chat.startswith('+') and len(chat) > 2:
                group_chats.append(chat)
        
        print(f"Found {len(group_chats)} named group chats:")
        print()
        
        for i, chat in enumerate(sorted(group_chats), 1):
            print(f"{i:2d}. '{chat}'")
        
        print(f"\n🎯 Currently configured chats:")
        for chat in Config.TARGET_CHATS:
            status = "✅ Found" if chat in chats else "❌ Not found"
            print(f"   - '{chat}' {status}")
            
        print(f"\n💡 Tip: Look for chats with names like:")
        print(f"   - Group chats with 'Push Back' in the name")
        print(f"   - Any other 1280-related chats")
        
    except Exception as e:
        print(f"❌ Error listing chats: {e}")

if __name__ == "__main__":
    list_all_chats()