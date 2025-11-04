"""iMessage chat parser for extracting conversation data."""

import sqlite3
import re
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path

class iMessageParser:
    """Parser for iMessage chat database."""
    
    def __init__(self, imessage_db_path: str, contact_map: Dict[str, str] = None):
        self.imessage_db_path = imessage_db_path
        self.contacts = {}
        self.contact_map = contact_map or {}
    
    def _get_imessage_connection(self):
        """Get connection to iMessage database."""
        if not Path(self.imessage_db_path).exists():
            raise FileNotFoundError(f"iMessage database not found at {self.imessage_db_path}")
        return sqlite3.connect(self.imessage_db_path)
    
    def _normalize_phone_number(self, phone: str) -> str:
        """Normalize phone number format."""
        if not phone:
            return ""
        # Remove all non-digits
        digits = re.sub(r'\D', '', phone)
        # If it's a 10-digit number, add US country code
        if len(digits) == 10:
            digits = "1" + digits
        return digits
    
    def get_chat_participants(self, chat_id: str) -> List[str]:
        """Get participants in a chat."""
        try:
            with self._get_imessage_connection() as conn:
                cursor = conn.execute('''
                    SELECT DISTINCT handle.id 
                    FROM handle
                    JOIN chat_handle_join ON handle.ROWID = chat_handle_join.handle_id
                    JOIN chat ON chat.ROWID = chat_handle_join.chat_id
                    WHERE chat.chat_identifier = ? OR chat.display_name = ?
                ''', (chat_id, chat_id))
                return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            print(f"Error getting chat participants: {e}")
            return []
    
    def get_chat_messages(self, chat_name: str, limit: int = 5000, months_back: int = 12) -> List[Dict]:
        """Extract messages from a specific chat within the specified time range."""
        messages = []
        
        # Calculate cutoff date (12 months ago)
        from datetime import datetime, timedelta
        cutoff_date = datetime.now() - timedelta(days=months_back * 30)
        cutoff_timestamp = (cutoff_date.timestamp() - 978307200) * 1000000000  # Convert to Core Data format
        
        try:
            with self._get_imessage_connection() as conn:
                # Query to get messages from a specific chat within time range
                cursor = conn.execute('''
                    SELECT 
                        message.text,
                        message.date,
                        message.is_from_me,
                        handle.id as sender_id,
                        chat.display_name as chat_name
                    FROM message
                    JOIN chat_message_join ON message.ROWID = chat_message_join.message_id
                    JOIN chat ON chat.ROWID = chat_message_join.chat_id
                    LEFT JOIN handle ON message.handle_id = handle.ROWID
                    WHERE (chat.chat_identifier LIKE ? OR chat.display_name LIKE ?)
                        AND message.text IS NOT NULL
                        AND LENGTH(message.text) > 0
                        AND message.date > ?
                    ORDER BY message.date DESC
                    LIMIT ?
                ''', (f'%{chat_name}%', f'%{chat_name}%', cutoff_timestamp, limit))
                
                for row in cursor.fetchall():
                    text, date, is_from_me, sender_id, chat_display_name = row
                    
                    # Convert Core Data timestamp to Python datetime
                    # Core Data timestamps are seconds since 2001-01-01
                    if date:
                        timestamp = datetime.fromtimestamp(date / 1000000000 + 978307200)
                    else:
                        timestamp = datetime.now()
                    
                    # Determine sender
                    if is_from_me:
                        sender = "You"
                    else:
                        sender = self._get_contact_name(sender_id) or sender_id or "Unknown"
                    
                    message = {
                        'chat_name': chat_display_name or chat_name,
                        'sender': sender,
                        'message_text': text,
                        'timestamp': timestamp,
                        'message_type': 'text'
                    }
                    messages.append(message)
                    
        except Exception as e:
            print(f"Error parsing chat '{chat_name}': {e}")
        
        return messages
    
    def _get_contact_name(self, handle_id: str) -> Optional[str]:
        """Get contact name from handle ID using contact mapping."""
        if not handle_id:
            return None
            
        # Try to get from cache
        if handle_id in self.contacts:
            return self.contacts[handle_id]
        
        # Clean up the handle ID and try contact mapping
        name = None
        
        if handle_id.startswith('+'):
            # Phone number - try to match with contact map
            clean_number = re.sub(r'\D', '', handle_id)  # Remove all non-digits
            
            # Try different variations of the number
            for contact_key, contact_name in self.contact_map.items():
                clean_key = re.sub(r'\D', '', contact_key)
                if clean_number.endswith(clean_key) or clean_key.endswith(clean_number):
                    name = contact_name
                    break
            
            if not name:
                # Format phone number nicely if no mapping found
                if len(clean_number) == 11 and clean_number.startswith('1'):
                    formatted = f"({clean_number[1:4]}) {clean_number[4:7]}-{clean_number[7:]}"
                elif len(clean_number) == 10:
                    formatted = f"({clean_number[:3]}) {clean_number[3:6]}-{clean_number[6:]}"
                else:
                    formatted = handle_id
                name = formatted
                
        elif '@' in handle_id:
            # Email address
            name = handle_id.split('@')[0].title()
        else:
            name = handle_id
        
        self.contacts[handle_id] = name
        return name
    
    def get_all_chat_names(self) -> List[str]:
        """Get all available chat names."""
        try:
            with self._get_imessage_connection() as conn:
                cursor = conn.execute('''
                    SELECT DISTINCT 
                        COALESCE(chat.display_name, chat.chat_identifier) as chat_name
                    FROM chat
                    WHERE chat_name IS NOT NULL
                    ORDER BY chat_name
                ''')
                return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            print(f"Error getting chat names: {e}")
            return []
    
    def find_embarrassing_messages(self, chat_name: str) -> List[Dict]:
        """Find potentially embarrassing messages for roast questions."""
        embarrassing_keywords = [
            'drunk', 'wasted', 'hangover', 'threw up', 'vomit',
            'embarrassing', 'awkward', 'cringe', 'regret',
            'oops', 'mistake', 'fail', 'disaster',
            'naked', 'underwear', 'bathroom', 'poop',
            'crush', 'dating', 'tinder', 'hookup',
            'broke', 'poor', 'debt', 'money',
            'cry', 'crying', 'tears', 'sad'
        ]
        
        messages = self.get_chat_messages(chat_name)
        embarrassing_messages = []
        
        for message in messages:
            text = message['message_text'].lower()
            if any(keyword in text for keyword in embarrassing_keywords):
                # Filter out very short messages
                if len(message['message_text']) > 20:
                    embarrassing_messages.append(message)
        
        return embarrassing_messages[:50]  # Limit results
    
    def find_funny_quotes(self, chat_name: str) -> List[Dict]:
        """Find funny/quotable messages."""
        messages = self.get_chat_messages(chat_name)
        funny_messages = []
        
        for message in messages:
            text = message['message_text']
            
            # Look for messages that might be funny
            conditions = [
                len(text) > 30 and len(text) < 200,  # Good length
                '!' in text or '?' in text,  # Has emotion
                not text.startswith('http'),  # Not just a link
                not re.match(r'^\d+$', text),  # Not just numbers
                not text.lower().startswith(('ok', 'yes', 'no', 'yeah', 'sure')),  # Not simple responses
            ]
            
            if all(conditions):
                funny_messages.append(message)
        
        return funny_messages[:100]  # Limit results
    
    def export_to_csv(self, chat_name: str, output_path: str):
        """Export chat messages to CSV for analysis."""
        import csv
        
        messages = self.get_chat_messages(chat_name)
        
        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['timestamp', 'sender', 'message_text', 'chat_name']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for message in messages:
                writer.writerow({
                    'timestamp': message['timestamp'].isoformat(),
                    'sender': message['sender'],
                    'message_text': message['message_text'],
                    'chat_name': message['chat_name']
                })
        
        print(f"Exported {len(messages)} messages to {output_path}")

# Example usage and testing
if __name__ == "__main__":
    # Test the parser (update path as needed)
    parser = iMessageParser("~/Library/Messages/chat.db")
    
    # Get available chats
    chats = parser.get_all_chat_names()
    print("Available chats:")
    for chat in chats[:10]:  # Show first 10
        print(f"  - {chat}")
    
    # Test parsing a specific chat
    if chats:
        test_chat = chats[0]
        messages = parser.get_chat_messages(test_chat, limit=5)
        print(f"\nSample messages from '{test_chat}':")
        for msg in messages:
            print(f"  {msg['sender']}: {msg['message_text'][:50]}...")