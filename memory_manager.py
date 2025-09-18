"""
Educational Poke Clone - Memory Manager
Handles user memory, conversation context, and preference storage.
"""

import asyncio
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import sqlite3
import os

@dataclass
class UserMemory:
    """Represents user memory data"""
    user_id: str
    preferences: Dict[str, Any]
    writing_style: Dict[str, Any]
    important_topics: List[str]
    conversation_summary: str
    last_updated: datetime

@dataclass
class ConversationContext:
    """Represents conversation context"""
    user_id: str
    conversation_id: str
    messages: List[Dict]
    summary: str
    created_at: datetime

class MemoryManager:
    """
    Memory manager for storing and retrieving user context, preferences, and conversation history.
    Implements the memory system described in the Poke prompts.
    """
    
    def __init__(self, db_path: str = "poke_memory.db"):
        self.db_path = db_path
        self._init_database()
        
    def _init_database(self):
        """Initialize the SQLite database for memory storage"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_memory (
                user_id TEXT PRIMARY KEY,
                preferences TEXT,
                writing_style TEXT,
                important_topics TEXT,
                conversation_summary TEXT,
                last_updated TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                conversation_id TEXT PRIMARY KEY,
                user_id TEXT,
                messages TEXT,
                summary TEXT,
                created_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user_memory (user_id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pending_confirmations (
                user_id TEXT PRIMARY KEY,
                confirmation_data TEXT,
                created_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user_memory (user_id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    async def get_user_context(self, user_id: str) -> Dict[str, Any]:
        """
        Get comprehensive user context including preferences, writing style, and conversation summary.
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT preferences, writing_style, important_topics, conversation_summary
                FROM user_memory WHERE user_id = ?
            """, (user_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                preferences, writing_style, important_topics, conversation_summary = result
                return {
                    "preferences": json.loads(preferences) if preferences else {},
                    "writing_style": json.loads(writing_style) if writing_style else {},
                    "important_topics": json.loads(important_topics) if important_topics else [],
                    "conversation_summary": conversation_summary or ""
                }
            else:
                # Return default context for new user
                return {
                    "preferences": {},
                    "writing_style": {},
                    "important_topics": [],
                    "conversation_summary": ""
                }
                
        except Exception as e:
            print(f"Error getting user context: {e}")
            return {
                "preferences": {},
                "writing_style": {},
                "important_topics": [],
                "conversation_summary": ""
            }
    
    async def update_user_memory(self, user_id: str, interaction: Dict[str, Any]) -> bool:
        """
        Update user memory with new interaction data.
        """
        try:
            # Get current memory
            current_context = await self.get_user_context(user_id)
            
            # Extract preferences from interaction
            preferences = self._extract_preferences(interaction, current_context["preferences"])
            
            # Extract writing style
            writing_style = self._extract_writing_style(interaction, current_context["writing_style"])
            
            # Extract important topics
            important_topics = self._extract_important_topics(interaction, current_context["important_topics"])
            
            # Update conversation summary
            conversation_summary = self._update_conversation_summary(
                interaction, current_context["conversation_summary"]
            )
            
            # Store updated memory
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO user_memory 
                (user_id, preferences, writing_style, important_topics, conversation_summary, last_updated)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                json.dumps(preferences),
                json.dumps(writing_style),
                json.dumps(important_topics),
                conversation_summary,
                datetime.now().isoformat()
            ))
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            print(f"Error updating user memory: {e}")
            return False
    
    def _extract_preferences(self, interaction: Dict, current_preferences: Dict) -> Dict:
        """Extract user preferences from interaction"""
        preferences = current_preferences.copy()
        
        # Extract communication preferences
        user_message = interaction.get("user_message", "")
        if "don't" in user_message.lower() or "stop" in user_message.lower():
            if "notifications" in user_message.lower():
                preferences["notifications"] = False
            if "emails" in user_message.lower():
                preferences["email_notifications"] = False
        
        # Extract time preferences
        if "morning" in user_message.lower():
            preferences["preferred_time"] = "morning"
        elif "evening" in user_message.lower():
            preferences["preferred_time"] = "evening"
        
        # Extract response style preferences
        if len(user_message) < 20:
            preferences["prefers_concise"] = True
        elif len(user_message) > 100:
            preferences["prefers_detailed"] = True
        
        return preferences
    
    def _extract_writing_style(self, interaction: Dict, current_style: Dict) -> Dict:
        """Extract user's writing style from interaction"""
        style = current_style.copy()
        user_message = interaction.get("user_message", "")
        
        # Analyze capitalization
        if user_message.islower():
            style["uses_lowercase"] = True
        elif user_message.isupper():
            style["uses_uppercase"] = True
        
        # Analyze punctuation
        if "!!" in user_message:
            style["uses_double_exclamation"] = True
        if "..." in user_message:
            style["uses_ellipsis"] = True
        
        # Analyze emoji usage
        emoji_count = sum(1 for char in user_message if ord(char) > 127)
        if emoji_count > 0:
            style["uses_emojis"] = True
            style["emoji_frequency"] = emoji_count / len(user_message)
        
        # Analyze sentence structure
        sentences = user_message.split(".")
        if len(sentences) > 1:
            avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences)
            style["avg_sentence_length"] = avg_sentence_length
        
        return style
    
    def _extract_important_topics(self, interaction: Dict, current_topics: List[str]) -> List[str]:
        """Extract important topics from interaction"""
        topics = current_topics.copy()
        user_message = interaction.get("user_message", "").lower()
        
        # Define topic keywords
        topic_keywords = {
            "work": ["job", "work", "office", "meeting", "project", "deadline"],
            "family": ["family", "mom", "dad", "sister", "brother", "parents"],
            "health": ["doctor", "health", "medical", "appointment", "exercise"],
            "travel": ["trip", "vacation", "flight", "hotel", "travel"],
            "finance": ["money", "budget", "payment", "bill", "expense"]
        }
        
        for topic, keywords in topic_keywords.items():
            if any(keyword in user_message for keyword in keywords):
                if topic not in topics:
                    topics.append(topic)
        
        return topics[:10]  # Limit to 10 topics
    
    def _update_conversation_summary(self, interaction: Dict, current_summary: str) -> str:
        """Update conversation summary with new interaction"""
        user_message = interaction.get("user_message", "")
        agent_response = interaction.get("agent_response", "")
        
        # Simple summary update (in reality, you'd use more sophisticated summarization)
        new_summary_parts = []
        
        if current_summary:
            new_summary_parts.append(current_summary)
        
        if user_message:
            new_summary_parts.append(f"User: {user_message[:100]}...")
        
        if agent_response:
            new_summary_parts.append(f"Agent: {agent_response[:100]}...")
        
        return " | ".join(new_summary_parts[-5:])  # Keep last 5 interactions
    
    async def store_conversation(self, user_id: str, conversation_id: str, messages: List[Dict]) -> bool:
        """Store a conversation in memory"""
        try:
            # Create conversation summary
            summary = self._create_conversation_summary(messages)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO conversations 
                (conversation_id, user_id, messages, summary, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (
                conversation_id,
                user_id,
                json.dumps(messages),
                summary,
                datetime.now().isoformat()
            ))
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            print(f"Error storing conversation: {e}")
            return False
    
    def _create_conversation_summary(self, messages: List[Dict]) -> str:
        """Create a summary of a conversation"""
        if not messages:
            return ""
        
        # Simple summarization (in reality, use AI summarization)
        user_messages = [msg for msg in messages if msg.get("role") == "user"]
        agent_messages = [msg for msg in messages if msg.get("role") == "assistant"]
        
        summary_parts = []
        if user_messages:
            summary_parts.append(f"User discussed: {user_messages[-1].get('content', '')[:50]}...")
        if agent_messages:
            summary_parts.append(f"Agent helped with: {agent_messages[-1].get('content', '')[:50]}...")
        
        return " | ".join(summary_parts)
    
    async def get_pending_confirmation(self, user_id: str) -> Optional[Dict]:
        """Get pending confirmation for a user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT confirmation_data FROM pending_confirmations WHERE user_id = ?
            """, (user_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return json.loads(result[0])
            return None
            
        except Exception as e:
            print(f"Error getting pending confirmation: {e}")
            return None
    
    async def set_pending_confirmation(self, user_id: str, confirmation_data: Dict) -> bool:
        """Set pending confirmation for a user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO pending_confirmations 
                (user_id, confirmation_data, created_at)
                VALUES (?, ?, ?)
            """, (
                user_id,
                json.dumps(confirmation_data),
                datetime.now().isoformat()
            ))
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            print(f"Error setting pending confirmation: {e}")
            return False
    
    async def clear_pending_confirmation(self, user_id: str) -> bool:
        """Clear pending confirmation for a user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                DELETE FROM pending_confirmations WHERE user_id = ?
            """, (user_id,))
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            print(f"Error clearing pending confirmation: {e}")
            return False
    
    async def get_conversation_history(self, user_id: str, limit: int = 10) -> List[Dict]:
        """Get recent conversation history for a user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT messages, summary, created_at 
                FROM conversations 
                WHERE user_id = ? 
                ORDER BY created_at DESC 
                LIMIT ?
            """, (user_id, limit))
            
            results = cursor.fetchall()
            conn.close()
            
            conversations = []
            for messages, summary, created_at in results:
                conversations.append({
                    "messages": json.loads(messages),
                    "summary": summary,
                    "created_at": created_at
                })
            
            return conversations
            
        except Exception as e:
            print(f"Error getting conversation history: {e}")
            return []

# Example usage
async def main():
    """Example of how to use the MemoryManager"""
    memory = MemoryManager()
    
    # Get user context
    context = await memory.get_user_context("user123")
    print(f"User context: {context}")
    
    # Update memory with interaction
    interaction = {
        "user_message": "hi there! how are you?",
        "agent_response": "I'm doing great! How can I help you today?",
        "timestamp": datetime.now().isoformat()
    }
    
    success = await memory.update_user_memory("user123", interaction)
    print(f"Memory update success: {success}")

if __name__ == "__main__":
    asyncio.run(main())

