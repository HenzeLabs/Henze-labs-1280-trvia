#!/usr/bin/env python3
"""
Parse the specific "It's Only Gay If You Push Back " chat (with trailing space).
"""

import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_path = Path(__file__).parent / 'backend'
sys.path.insert(0, str(backend_path))

from app.models import Database, Message
from app.parsers.imessage_parser import iMessageParser
from app.config import Config

def parse_specific_chat():
    """Parse the exact chat name found in the database."""
    
    print("🔍 Trying to parse the exact chat name found...")
    
    # Initialize database
    db = Database(str(Config.DATABASE_PATH))
    message_model = Message(db)
    
    # Initialize parser with contact mapping
    parser = iMessageParser(str(Config.IMESSAGE_DB_PATH), Config.CONTACT_MAP)
    
    # Try the exact chat name with trailing space (as found in database)
    exact_chat_name = "It's Only Gay If You Push Back "
    
    print(f"📱 Parsing: '{exact_chat_name}'")
    
    try:
        messages = parser.get_chat_messages(exact_chat_name, limit=1000, months_back=12)
        
        if messages:
            # Store messages in database
            stored_count = 0
            for message in messages:
                try:
                    message_model.add_message(
                        chat_name=exact_chat_name,
                        sender=message['sender'],
                        message_text=message['message_text'],
                        timestamp=message['timestamp'],
                        message_type=message['message_type']
                    )
                    stored_count += 1
                except Exception as e:
                    # Skip duplicate or problematic messages
                    continue
            
            print(f"✅ Successfully stored {stored_count} messages from '{exact_chat_name}'")
            
            # Show sample participants
            senders = list(set(m['sender'] for m in messages[:100]))
            print(f"👥 Participants: {', '.join(senders[:5])}")
            
            return stored_count
        else:
            print(f"❌ No messages found for '{exact_chat_name}'")
            return 0
            
    except Exception as e:
        print(f"❌ Error parsing '{exact_chat_name}': {e}")
        return 0

if __name__ == "__main__":
    parse_specific_chat()