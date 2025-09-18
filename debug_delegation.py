#!/usr/bin/env python3
"""
Debug script to test delegation logic
"""

def should_delegate_to_execution_agent(message: str) -> bool:
    """Test the delegation logic"""
    execution_keywords = [
        # Email operations
        "send email", "compose email", "email to", "check email", "read email",
        # Calendar operations  
        "schedule", "calendar", "meeting", "event", "appointment",
        # Search operations
        "search", "find", "look for", "show me",
        # Authentication and setup
        "connect", "authenticate", "auth", "login", "access", "permission",
        "gmail", "google", "calendar", "email account",
        # Task operations
        "remind me", "set reminder", "automation", "trigger",
        "create", "delete", "update", "edit", "manage",
        # General assistance that needs tools
        "help me with", "can you", "need access", "set up"
    ]
    
    message_lower = message.lower()
    matches = [keyword for keyword in execution_keywords if keyword in message_lower]
    
    print(f"Message: '{message}'")
    print(f"Message lower: '{message_lower}'")
    print(f"Matching keywords: {matches}")
    print(f"Should delegate: {len(matches) > 0}")
    print("-" * 50)
    
    return any(keyword in message_lower for keyword in execution_keywords)

# Test cases
test_messages = [
    "connect my Gmail",
    "connect",
    "help me connect my Gmail",
    "I want to connect to Google",
    "authenticate my email",
    "help me with email",
    "send an email"
]

for msg in test_messages:
    should_delegate_to_execution_agent(msg)
