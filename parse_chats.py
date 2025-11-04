#!/usr/bin/env python3
"""
Script to initialize the database and parse the 4 target group chats.
"""

import sys
import os
from pathlib import Path

# Add the backend directory to the Python path
backend_path = Path(__file__).parent / 'backend'
sys.path.insert(0, str(backend_path))

from app.models import Database, Message
from app.parsers.imessage_parser import iMessageParser
from app.config import Config

def main():
    """Initialize DB and parse target chats."""
    
    # Check if chat.db exists
    if not Path('chat.db').exists():
        print("❌ Error: chat.db not found in project root")
        print("Please copy your iMessage database to ./chat.db")
        return
    
    print("🚀 Initializing 1280 Trivia database...")
    
    # Initialize database
    db = Database(str(Config.DATABASE_PATH))
    message_model = Message(db)
    
    print(f"✅ Database initialized at: {Config.DATABASE_PATH}")
    
    # Initialize parser with contact mapping
    parser = iMessageParser(str(Config.IMESSAGE_DB_PATH), Config.CONTACT_MAP)
    
    print("📱 Parsing target group chats (last 12 months)...")
    
    # Parse each target chat
    total_messages = 0
    chat_stats = {}
    
    for chat_name in Config.TARGET_CHATS:
        print(f"\n🔍 Searching for chat: '{chat_name}'")
        
        try:
            # Get messages from this chat (last 12 months)
            messages = parser.get_chat_messages(chat_name, limit=2000, months_back=12)
            
            if not messages:
                print(f"⚠️  No messages found for '{chat_name}' - trying partial match...")
                
                # Try to find chats with partial name match
                all_chats = parser.get_all_chat_names()
                matches = [c for c in all_chats if any(word.lower() in c.lower() for word in chat_name.split())]
                
                if matches:
                    print(f"   Found similar chats: {matches[:3]}")
                    # Try the first match
                    messages = parser.get_chat_messages(matches[0], limit=2000, months_back=12)
                    if messages:
                        chat_name = matches[0]  # Update to actual chat name
                        print(f"   ✅ Using '{chat_name}' instead")
            
            if messages:
                # Store messages in database
                stored_count = 0
                for message in messages:
                    try:
                        message_model.add_message(
                            chat_name=chat_name,
                            sender=message['sender'],
                            message_text=message['message_text'],
                            timestamp=message['timestamp'],
                            message_type=message['message_type']
                        )
                        stored_count += 1
                    except Exception as e:
                        # Skip duplicate or problematic messages
                        continue
                
                chat_stats[chat_name] = stored_count
                total_messages += stored_count
                print(f"   ✅ Stored {stored_count} messages from '{chat_name}'")
                
                # Show sample senders
                senders = list(set(m['sender'] for m in messages[:100]))
                print(f"   👥 Participants: {', '.join(senders[:5])}")
                
            else:
                print(f"   ❌ No messages found for '{chat_name}'")
                
        except Exception as e:
            print(f"   ❌ Error parsing '{chat_name}': {e}")
    
    print(f"\n📊 Parsing complete!")
    print(f"   Total messages stored: {total_messages}")
    print(f"   Chats processed: {len(chat_stats)}")
    
    for chat, count in chat_stats.items():
        print(f"   - {chat}: {count} messages")
    
    if total_messages > 0:
        print(f"\n🎯 Ready to generate questions!")
        print(f"   Next step: Run the admin panel to generate questions")
        print(f"   Or run: python -c \"from generate_questions import generate_sample_questions; generate_sample_questions()\"")
    else:
        print(f"\n⚠️  No messages were imported. Check your chat names and try again.")
        print(f"   Available chats in your database:")
        try:
            all_chats = parser.get_all_chat_names()
            for chat in all_chats[:10]:
                print(f"   - {chat}")
        except Exception as e:
            print(f"   Error listing chats: {e}")

if __name__ == "__main__":
    main()