"""
Educational Poke Clone - Message Router
Handles communication between agents.
"""

import asyncio
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass

@dataclass
class Message:
    """Represents a message between agents"""
    id: str
    sender: str
    recipient: str
    content: str
    message_type: str
    timestamp: datetime
    metadata: Dict = None

class MessageRouter:
    """
    Message router for handling communication between agents.
    """
    
    def __init__(self):
        self.message_queue = []
        self.agent_registry = {}
        
    def register_agent(self, agent_id: str, agent_instance):
        """Register an agent with the router"""
        self.agent_registry[agent_id] = agent_instance
        
    async def send_message(self, sender: str, recipient: str, content: str, message_type: str = "task") -> str:
        """Send a message between agents"""
        try:
            message_id = f"msg_{datetime.now().timestamp()}"
            
            message = Message(
                id=message_id,
                sender=sender,
                recipient=recipient,
                content=content,
                message_type=message_type,
                timestamp=datetime.now()
            )
            
            self.message_queue.append(message)
            
            # Process the message if recipient is registered
            if recipient in self.agent_registry:
                await self._process_message(message)
            
            return message_id
            
        except Exception as e:
            print(f"Error sending message: {e}")
            return None
    
    async def _process_message(self, message: Message):
        """Process a message by delivering it to the recipient"""
        try:
            recipient_agent = self.agent_registry.get(message.recipient)
            if recipient_agent:
                # Deliver the message to the agent
                if hasattr(recipient_agent, 'handle_message'):
                    await recipient_agent.handle_message(message)
                else:
                    print(f"Agent {message.recipient} doesn't have handle_message method")
            
        except Exception as e:
            print(f"Error processing message: {e}")
    
    async def get_messages_for_agent(self, agent_id: str) -> List[Message]:
        """Get all messages for a specific agent"""
        agent_messages = []
        for message in self.message_queue:
            if message.recipient == agent_id:
                agent_messages.append(message)
        
        return agent_messages
    
    async def get_message_history(self, agent_id: str, limit: int = 10) -> List[Dict]:
        """Get message history for an agent"""
        messages = await self.get_messages_for_agent(agent_id)
        
        # Sort by timestamp and limit
        messages.sort(key=lambda x: x.timestamp, reverse=True)
        limited_messages = messages[:limit]
        
        return [
            {
                "id": msg.id,
                "sender": msg.sender,
                "content": msg.content,
                "message_type": msg.message_type,
                "timestamp": msg.timestamp.isoformat()
            }
            for msg in limited_messages
        ]

