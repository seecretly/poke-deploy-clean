"""
Educational Poke Clone - Main Agent
This is the user-facing conversational interface that handles user interactions
and delegates tasks to the execution agent.
"""

import asyncio
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import openai
from execution_agent import ExecutionAgent
from memory_manager import MemoryManager
from message_router import MessageRouter

@dataclass
class UserMessage:
    """Represents a message from the user"""
    content: str
    timestamp: datetime
    user_id: str
    message_type: str = "user"

@dataclass
class AgentResponse:
    """Represents a response from an agent"""
    content: str
    timestamp: datetime
    agent_type: str
    message_type: str = "agent"

class MainPokeAgent:
    """
    Main Poke Agent - The conversational interface users interact with.
    Handles personality, conversation flow, and task delegation.
    """
    
    def __init__(self, openai_api_key: str):
        self.openai_client = openai.OpenAI(api_key=openai_api_key)
        self.execution_agent = ExecutionAgent()
        self.memory_manager = MemoryManager()
        self.message_router = MessageRouter()
        self.conversation_history = []
        
    async def process_user_message(self, user_id: str, message: str) -> str:
        """
        Process a user message and return a response.
        This is the main entry point for user interactions.
        """
        # Create user message object
        user_msg = UserMessage(
            content=message,
            timestamp=datetime.now(),
            user_id=user_id
        )
        
        # Add to conversation history
        self.conversation_history.append(user_msg)
        
        # Get user context and memory
        user_context = await self.memory_manager.get_user_context(user_id)
        
        # Determine if this needs delegation to execution agent
        needs_execution = self._should_delegate_to_execution_agent(message)
        
        if needs_execution:
            # Delegate to execution agent
            execution_result = await self.execution_agent.process_task(
                task_description=message,
                user_id=user_id,
                context=user_context
            )
            
            # Process the execution result
            response = await self._process_execution_result(execution_result, user_msg)
        else:
            # Handle conversational response
            response = await self._generate_conversational_response(user_msg, user_context)
        
        # Update memory with this interaction
        await self.memory_manager.update_user_memory(
            user_id=user_id,
            interaction={
                "user_message": message,
                "agent_response": response,
                "timestamp": datetime.now().isoformat()
            }
        )
        
        return response
    
    def _should_delegate_to_execution_agent(self, message: str) -> bool:
        """
        Determine if a message should be delegated to the execution agent.
        Look for keywords that indicate task execution is needed.
        """
        execution_keywords = [
            "send email", "compose email", "email to",
            "schedule", "calendar", "meeting", "event",
            "search", "find", "look for",
            "remind me", "set reminder", "automation",
            "create", "delete", "update", "edit"
        ]
        
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in execution_keywords)
    
    async def _process_execution_result(self, execution_result: Dict, user_msg: UserMessage) -> str:
        """
        Process the result from the execution agent and format for user.
        """
        if execution_result.get("needs_confirmation"):
            # Show draft for confirmation
            return self._format_draft_confirmation(execution_result)
        elif execution_result.get("task_completed"):
            # Task was completed successfully
            return self._format_completion_message(execution_result)
        else:
            # Return information found
            return self._format_information_response(execution_result)
    
    def _format_draft_confirmation(self, execution_result: Dict) -> str:
        """Format a draft for user confirmation"""
        draft = execution_result.get("draft", {})
        draft_type = draft.get("type", "email")
        
        if draft_type == "email":
            return f"""
📧 **Email Draft**

**To:** {draft.get('to', '')}
**Subject:** {draft.get('subject', '')}

**Message:**
{draft.get('body', '')}

Does this look good to send? 👍 or 👎
            """.strip()
        elif draft_type == "calendar":
            return f"""
📅 **Calendar Event Draft**

**Title:** {draft.get('title', '')}
**Date:** {draft.get('date', '')}
**Time:** {draft.get('time', '')}
**Description:** {draft.get('description', '')}

Does this look good to create? 👍 or 👎
            """.strip()
    
    def _format_completion_message(self, execution_result: Dict) -> str:
        """Format a task completion message"""
        task_type = execution_result.get("task_type", "task")
        details = execution_result.get("details", "")
        
        if task_type == "email_sent":
            return f"✅ Email sent successfully! {details}"
        elif task_type == "calendar_created":
            return f"✅ Calendar event created! {details}"
        else:
            return f"✅ {task_type.replace('_', ' ').title()} completed! {details}"
    
    def _format_information_response(self, execution_result: Dict) -> str:
        """Format information found by execution agent"""
        results = execution_result.get("results", [])
        if not results:
            return "I couldn't find anything matching your request."
        
        response = "Here's what I found:\n\n"
        for i, result in enumerate(results[:5], 1):  # Limit to 5 results
            response += f"{i}. {result.get('summary', 'No summary available')}\n"
        
        return response.strip()
    
    async def _generate_conversational_response(self, user_msg: UserMessage, user_context: Dict) -> str:
        """
        Generate a conversational response using the Poke personality.
        This handles non-task conversations with the user's personality.
        """
        # Get conversation history for context
        recent_messages = self.conversation_history[-5:]  # Last 5 messages
        
        # Build context for the AI
        context_messages = [
            {
                "role": "system",
                "content": self._get_personality_prompt(user_context)
            }
        ]
        
        # Add recent conversation history
        for msg in recent_messages:
            if isinstance(msg, UserMessage):
                context_messages.append({
                    "role": "user",
                    "content": msg.content
                })
            elif isinstance(msg, AgentResponse):
                context_messages.append({
                    "role": "assistant", 
                    "content": msg.content
                })
        
        # Generate response
        response = await self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=context_messages,
            temperature=0.7,
            max_tokens=500
        )
        
        return response.choices[0].message.content
    
    def _get_personality_prompt(self, user_context: Dict) -> str:
        """
        Get the COMPLETE personality prompt based on user context and preferences.
        This implements the FULL Poke personality from the original system prompts.
        """
        # Load the complete Poke system prompt
        try:
            with open('COMPLETE_POKE_SYSTEM_PROMPT.txt', 'r') as f:
                base_personality = f.read()
        except FileNotFoundError:
            # Fallback to a comprehensive prompt if file not found
            base_personality = """You are Poke, and you were developed by The Interaction Company of California, a Palo Alto-based AI startup (short name: Interaction). You interact with users through text messages via iMessage/WhatsApp/SMS and have access to a wide range of tools.

IMPORTANT: Whenever the user asks for information, you always assume you are capable of finding it. If the user asks for something you don't know about, the agent can find it. The agent also has full browser-use capabilities, which you can use to accomplish interactive tasks.

IMPORTANT: Make sure you get user confirmation before sending, forwarding, or replying to emails. You should always show the user drafts before they're sent.

Personality:
When speaking, be witty and warm, though never overdo it. You should sound like a friend and appear to genuinely enjoy talking to the user. Find a balance that sounds natural, and never be sycophantic. Be warm when the user actually deserves it or needs it.

Aim to be subtly witty, humorous, and sarcastic when fitting the texting vibe. It should feel natural and conversational. Never force jokes when a normal response would be more appropriate.

Tone & Style:
- Never output preamble or postamble
- Never include unnecessary details when conveying information, except possibly for humor  
- Never ask the user if they want extra detail or additional tasks
- IMPORTANT: Never say "Let me know if you need anything else"
- IMPORTANT: Never say "Anything specific you want to know"
- Adapt to the texting style of the user. Use lowercase if the user does
- Never use obscure acronyms or slang if the user has not first
- IMPORTANT: Never text with emojis if the user has not texted them first
- You must match your response length approximately to the user's
- Sound like a friend rather than a traditional chatbot
- Prefer not to use corporate jargon or overly formal language
- When the user is just chatting, do not unnecessarily offer help; humor or sass is better

You have access to Gmail API for email management, Google Calendar API for scheduling, web browsing capabilities, various integrations (Notion, Linear, etc.), and memory system for user preferences. Always be proactive in offering help and suggesting next steps."""
        
        # Add user-specific context if available
        if user_context.get("preferences"):
            base_personality += f"\n\nUser preferences: {user_context['preferences']}"
        
        if user_context.get("writing_style"):
            base_personality += f"\n\nUser's writing style: {user_context['writing_style']}"
        
        return base_personality
    
    async def handle_emoji_reaction(self, user_id: str, reaction: str) -> str:
        """
        Handle emoji reactions from the user.
        Positive reactions = yes, negative reactions = no.
        """
        # Get the last pending confirmation
        pending_confirmation = await self.memory_manager.get_pending_confirmation(user_id)
        
        if not pending_confirmation:
            return "I don't have anything pending for confirmation."
        
        # Determine if reaction is positive or negative
        positive_emojis = ["👍", "❤️", "😊", "🎉", "✅", "👌"]
        negative_emojis = ["👎", "😡", "❌", "🤮", "👎"]
        
        is_positive = reaction in positive_emojis
        is_negative = reaction in negative_emojis
        
        if is_positive:
            # Execute the pending action
            result = await self.execution_agent.execute_confirmed_action(
                pending_confirmation, user_id
            )
            await self.memory_manager.clear_pending_confirmation(user_id)
            return self._format_completion_message(result)
        elif is_negative:
            # Cancel the pending action
            await self.memory_manager.clear_pending_confirmation(user_id)
            return "Got it, I won't proceed with that."
        else:
            return "I'm not sure what that reaction means. Please use 👍 for yes or 👎 for no."

# Example usage
async def main():
    """Example of how to use the MainPokeAgent"""
    agent = MainPokeAgent(openai_api_key="your-api-key")
    
    # Simulate user interaction
    response = await agent.process_user_message(
        user_id="user123",
        message="Send an email to john@example.com about the meeting tomorrow"
    )
    
    print(f"Agent response: {response}")

if __name__ == "__main__":
    asyncio.run(main())

