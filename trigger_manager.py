"""
Educational Poke Clone - Trigger Manager
Handles triggers, automations, and reminders.
"""

import asyncio
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass

@dataclass
class Trigger:
    """Represents a trigger/automation"""
    id: str
    user_id: str
    trigger_type: str  # "email", "cron", "reminder"
    condition: str
    action: str
    active: bool = True
    created_at: datetime = None

class TriggerManager:
    """
    Trigger manager for handling automations and reminders.
    """
    
    def __init__(self):
        self.triggers = {}  # Simple in-memory storage for demo
        
    async def create_reminder(self, user_id: str, message: str, trigger_time: str, recurring: bool = False) -> Dict:
        """Create a time-based reminder trigger"""
        try:
            trigger_id = f"reminder_{datetime.now().timestamp()}"
            
            trigger = Trigger(
                id=trigger_id,
                user_id=user_id,
                trigger_type="cron",
                condition=trigger_time,
                action=f"Remind user: {message}",
                created_at=datetime.now()
            )
            
            self.triggers[trigger_id] = trigger
            
            return {
                "success": True,
                "trigger_id": trigger_id,
                "details": f"Reminder set for {trigger_time}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def create_email_automation(self, user_id: str, condition: str, action: str) -> Dict:
        """Create an email-based automation trigger"""
        try:
            trigger_id = f"automation_{datetime.now().timestamp()}"
            
            trigger = Trigger(
                id=trigger_id,
                user_id=user_id,
                trigger_type="email",
                condition=condition,
                action=action,
                created_at=datetime.now()
            )
            
            self.triggers[trigger_id] = trigger
            
            return {
                "success": True,
                "trigger_id": trigger_id,
                "details": "Email automation created"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_user_triggers(self, user_id: str) -> List[Dict]:
        """Get all triggers for a user"""
        user_triggers = []
        for trigger in self.triggers.values():
            if trigger.user_id == user_id:
                user_triggers.append({
                    "id": trigger.id,
                    "type": trigger.trigger_type,
                    "condition": trigger.condition,
                    "action": trigger.action,
                    "active": trigger.active,
                    "created_at": trigger.created_at.isoformat()
                })
        
        return user_triggers
    
    async def delete_trigger(self, trigger_id: str, user_id: str) -> Dict:
        """Delete a trigger"""
        try:
            if trigger_id in self.triggers:
                trigger = self.triggers[trigger_id]
                if trigger.user_id == user_id:
                    del self.triggers[trigger_id]
                    return {
                        "success": True,
                        "details": f"Trigger {trigger_id} deleted"
                    }
                else:
                    return {
                        "success": False,
                        "error": "Trigger not found or access denied"
                    }
            else:
                return {
                    "success": False,
                    "error": "Trigger not found"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def check_triggers(self, user_id: str, trigger_type: str = None) -> List[Dict]:
        """Check for triggered automations"""
        triggered = []
        
        for trigger in self.triggers.values():
            if trigger.user_id == user_id and trigger.active:
                if trigger_type is None or trigger.trigger_type == trigger_type:
                    # Simple trigger checking (in real implementation, use proper scheduling)
                    triggered.append({
                        "trigger_id": trigger.id,
                        "action": trigger.action,
                        "condition": trigger.condition
                    })
        
        return triggered

