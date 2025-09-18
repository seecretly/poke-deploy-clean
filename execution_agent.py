"""
Educational Poke Clone - Execution Agent
This is the "execution engine" that performs actual tasks like email management,
calendar operations, and integrations. It doesn't interact directly with users.
"""

import asyncio
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import openai
from email_service import EmailService
from calendar_service import CalendarService
from trigger_manager import TriggerManager
from integration_manager import IntegrationManager

@dataclass
class TaskResult:
    """Result of a task execution"""
    success: bool
    data: Dict[str, Any]
    needs_confirmation: bool = False
    draft: Optional[Dict] = None
    error_message: Optional[str] = None

class ExecutionAgent:
    """
    Execution Agent - The "execution engine" that performs tasks.
    Handles email, calendar, integrations, and other operations.
    """
    
    def __init__(self):
        self.email_service = EmailService()
        self.calendar_service = CalendarService()
        self.trigger_manager = TriggerManager()
        self.integration_manager = IntegrationManager()
        # OpenAI API key is set globally in main_poke_agent
        
    async def process_task(self, task_description: str, user_id: str, context: Dict) -> Dict:
        """
        Process a task and return the result.
        This is the main entry point for task execution.
        """
        # Analyze the task to determine what needs to be done
        task_analysis = await self._analyze_task(task_description, context)
        
        # Execute the appropriate action based on task type
        if task_analysis["task_type"] == "email":
            return await self._handle_email_task(task_analysis, user_id)
        elif task_analysis["task_type"] == "calendar":
            return await self._handle_calendar_task(task_analysis, user_id)
        elif task_analysis["task_type"] == "search":
            return await self._handle_search_task(task_analysis, user_id)
        elif task_analysis["task_type"] == "trigger":
            return await self._handle_trigger_task(task_analysis, user_id)
        elif task_analysis["task_type"] == "integration":
            return await self._handle_integration_task(task_analysis, user_id)
        elif task_analysis["task_type"] == "authentication":
            return await self._handle_authentication_task(task_analysis, user_id)
        else:
            return {
                "success": False,
                "error": "Unknown task type",
                "task_type": "unknown"
            }
    
    async def _analyze_task(self, task_description: str, context: Dict) -> Dict:
        """
        Analyze a task description to determine what needs to be done.
        Uses AI to understand the user's intent.
        """
        analysis_prompt = f"""
Analyze this task request and determine what needs to be done:

Task: "{task_description}"
User Context: {json.dumps(context, indent=2)}

Determine:
1. Task type (email, calendar, search, trigger, integration, authentication, other)
2. Specific action needed
3. Required parameters
4. Whether confirmation is needed

Respond in JSON format:
{{
    "task_type": "email|calendar|search|trigger|integration|authentication|other",
    "action": "send|compose|search|create|delete|update|schedule|remind|connect|authenticate",
    "parameters": {{
        "recipient": "email@example.com",
        "subject": "Email subject",
        "body": "Email body",
        "date": "2024-01-01",
        "time": "14:00",
        "query": "search terms",
        "service": "gmail|calendar|google"
    }},
    "needs_confirmation": true/false,
    "confidence": 0.0-1.0
}}
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": analysis_prompt}],
            temperature=0.1
        )
        
        try:
            return json.loads(response.choices[0].message.content)
        except json.JSONDecodeError:
            return {
                "task_type": "other",
                "action": "unknown",
                "parameters": {},
                "needs_confirmation": True,
                "confidence": 0.0
            }
    
    async def _handle_email_task(self, task_analysis: Dict, user_id: str) -> Dict:
        """Handle email-related tasks"""
        action = task_analysis.get("action", "")
        parameters = task_analysis.get("parameters", {})
        
        # Check if user is authenticated for Gmail first
        # In a real implementation, this would check stored credentials
        # For now, we'll assume they need authentication
        has_gmail_auth = await self._check_gmail_authentication(user_id)
        
        if not has_gmail_auth:
            # Redirect to authentication
            return await self._handle_authentication_task({
                "task_type": "authentication",
                "action": "authenticate", 
                "parameters": {"service": "gmail"}
            }, user_id)
        
        if action == "send":
            # Compose and send email
            draft = {
                "type": "email",
                "to": parameters.get("recipient", ""),
                "subject": parameters.get("subject", ""),
                "body": parameters.get("body", ""),
                "user_id": user_id
            }
            
            return {
                "needs_confirmation": True,
                "draft": draft,
                "task_type": "email_compose"
            }
        
        elif action == "search":
            # Search emails
            query = parameters.get("query", "")
            results = await self.email_service.search_emails(user_id, query)
            
            return {
                "success": True,
                "task_type": "email_search",
                "results": results
            }
        
        elif action == "compose":
            # Just compose without sending
            draft = {
                "type": "email",
                "to": parameters.get("recipient", ""),
                "subject": parameters.get("subject", ""),
                "body": parameters.get("body", ""),
                "user_id": user_id
            }
            
            return {
                "needs_confirmation": True,
                "draft": draft,
                "task_type": "email_compose"
            }
        
        else:
            return {
                "success": False,
                "error": f"Unknown email action: {action}",
                "task_type": "email"
            }
    
    async def _handle_calendar_task(self, task_analysis: Dict, user_id: str) -> Dict:
        """Handle calendar-related tasks"""
        action = task_analysis.get("action", "")
        parameters = task_analysis.get("parameters", {})
        
        # Check if user is authenticated for Calendar first
        has_calendar_auth = await self._check_calendar_authentication(user_id)
        
        if not has_calendar_auth:
            # Redirect to authentication
            return await self._handle_authentication_task({
                "task_type": "authentication",
                "action": "authenticate",
                "parameters": {"service": "calendar"}
            }, user_id)
        
        if action == "create":
            # Create calendar event
            draft = {
                "type": "calendar",
                "title": parameters.get("title", "New Event"),
                "date": parameters.get("date", ""),
                "time": parameters.get("time", ""),
                "description": parameters.get("description", ""),
                "user_id": user_id
            }
            
            return {
                "needs_confirmation": True,
                "draft": draft,
                "task_type": "calendar_create"
            }
        
        elif action == "search":
            # Search calendar events
            query = parameters.get("query", "")
            results = await self.calendar_service.search_events(user_id, query)
            
            return {
                "success": True,
                "task_type": "calendar_search",
                "results": results
            }
        
        else:
            return {
                "success": False,
                "error": f"Unknown calendar action: {action}",
                "task_type": "calendar"
            }
    
    async def _handle_search_task(self, task_analysis: Dict, user_id: str) -> Dict:
        """Handle search tasks across multiple sources"""
        query = task_analysis.get("parameters", {}).get("query", "")
        
        # Search multiple sources in parallel
        search_tasks = [
            self.email_service.search_emails(user_id, query),
            self.calendar_service.search_events(user_id, query),
            self.integration_manager.search_notion(user_id, query),
            self.integration_manager.search_linear(user_id, query)
        ]
        
        results = await asyncio.gather(*search_tasks, return_exceptions=True)
        
        # Combine results from all sources
        combined_results = []
        for i, result in enumerate(results):
            if not isinstance(result, Exception) and result:
                source = ["email", "calendar", "notion", "linear"][i]
                for item in result:
                    item["source"] = source
                    combined_results.append(item)
        
        return {
            "success": True,
            "task_type": "search",
            "results": combined_results
        }
    
    async def _handle_trigger_task(self, task_analysis: Dict, user_id: str) -> Dict:
        """Handle trigger/automation tasks"""
        action = task_analysis.get("action", "")
        parameters = task_analysis.get("parameters", {})
        
        if action == "remind":
            # Create a reminder trigger
            trigger = await self.trigger_manager.create_reminder(
                user_id=user_id,
                message=parameters.get("message", ""),
                trigger_time=parameters.get("time", ""),
                recurring=parameters.get("recurring", False)
            )
            
            return {
                "success": True,
                "task_type": "trigger_created",
                "details": f"Reminder set for {parameters.get('time', 'specified time')}",
                "trigger_id": trigger.get("id")
            }
        
        elif action == "automation":
            # Create an email automation
            trigger = await self.trigger_manager.create_email_automation(
                user_id=user_id,
                condition=parameters.get("condition", ""),
                action=parameters.get("action", "")
            )
            
            return {
                "success": True,
                "task_type": "automation_created",
                "details": "Email automation created",
                "trigger_id": trigger.get("id")
            }
        
        else:
            return {
                "success": False,
                "error": f"Unknown trigger action: {action}",
                "task_type": "trigger"
            }
    
    async def _handle_integration_task(self, task_analysis: Dict, user_id: str) -> Dict:
        """Handle integration tasks"""
        action = task_analysis.get("action", "")
        parameters = task_analysis.get("parameters", {})
        integration = parameters.get("integration", "")
        
        if integration == "notion":
            if action == "search":
                results = await self.integration_manager.search_notion(
                    user_id, parameters.get("query", "")
                )
                return {
                    "success": True,
                    "task_type": "notion_search",
                    "results": results
                }
        
        elif integration == "linear":
            if action == "search":
                results = await self.integration_manager.search_linear(
                    user_id, parameters.get("query", "")
                )
                return {
                    "success": True,
                    "task_type": "linear_search",
                    "results": results
                }
        
        return {
            "success": False,
            "error": f"Unknown integration or action: {integration}/{action}",
            "task_type": "integration"
        }
    
    async def _handle_authentication_task(self, task_analysis: Dict, user_id: str) -> Dict:
        """Handle authentication and connection requests"""
        action = task_analysis.get("action", "")
        parameters = task_analysis.get("parameters", {})
        service = parameters.get("service", "").lower()
        
        # Generate authentication URLs based on the service requested
        if "gmail" in service or "email" in service or "google" in service:
            # Generate Google OAuth URL for Gmail access
            import uuid
            auth_token = str(uuid.uuid4()).replace('-', '')
            
            # In a real implementation, this would generate a proper OAuth URL
            # For now, simulate the auth URL generation
            auth_url = f"https://web-production-d8e63.up.railway.app/auth-web?token={auth_token}&user_id={user_id}"
            
            return {
                "success": True,
                "task_type": "authentication",
                "service": "gmail",
                "auth_url": auth_url,
                "message": f"To access your Gmail, please click this authentication link: {auth_url}",
                "needs_user_action": True
            }
        
        elif "calendar" in service:
            # Generate Google Calendar OAuth URL
            import uuid
            auth_token = str(uuid.uuid4()).replace('-', '')
            
            auth_url = f"https://web-production-d8e63.up.railway.app/auth-web?token={auth_token}&user_id={user_id}&service=calendar"
            
            return {
                "success": True,
                "task_type": "authentication", 
                "service": "calendar",
                "auth_url": auth_url,
                "message": f"To access your Google Calendar, please click this authentication link: {auth_url}",
                "needs_user_action": True
            }
        
        else:
            return {
                "success": False,
                "error": f"Authentication not supported for service: {service}",
                "task_type": "authentication"
            }
    
    async def _check_gmail_authentication(self, user_id: str) -> bool:
        """Check if user has valid Gmail authentication"""
        # In a real implementation, this would check stored OAuth tokens
        # For educational purposes, we'll assume they need authentication
        # This can be enhanced to check actual stored credentials
        
        # Simulate checking stored credentials
        # Return False to always require authentication for demo
        return False
    
    async def _check_calendar_authentication(self, user_id: str) -> bool:
        """Check if user has valid Calendar authentication"""
        # In a real implementation, this would check stored OAuth tokens
        # For educational purposes, we'll assume they need authentication
        return False
    
    async def execute_confirmed_action(self, confirmation_data: Dict, user_id: str) -> Dict:
        """
        Execute an action that has been confirmed by the user.
        """
        action_type = confirmation_data.get("type", "")
        
        if action_type == "email":
            # Send the email
            result = await self.email_service.send_email(
                to=confirmation_data.get("to", ""),
                subject=confirmation_data.get("subject", ""),
                body=confirmation_data.get("body", ""),
                user_id=user_id
            )
            
            return {
                "success": result.get("success", False),
                "task_type": "email_sent",
                "details": f"Email sent to {confirmation_data.get('to', '')}",
                "message_id": result.get("message_id")
            }
        
        elif action_type == "calendar":
            # Create the calendar event
            result = await self.calendar_service.create_event(
                title=confirmation_data.get("title", ""),
                date=confirmation_data.get("date", ""),
                time=confirmation_data.get("time", ""),
                description=confirmation_data.get("description", ""),
                user_id=user_id
            )
            
            return {
                "success": result.get("success", False),
                "task_type": "calendar_created",
                "details": f"Event '{confirmation_data.get('title', '')}' created",
                "event_id": result.get("event_id")
            }
        
        else:
            return {
                "success": False,
                "error": f"Unknown action type: {action_type}",
                "task_type": "unknown"
            }

# Example usage
async def main():
    """Example of how to use the ExecutionAgent"""
    agent = ExecutionAgent()
    
    # Simulate task processing
    result = await agent.process_task(
        task_description="Send an email to john@example.com about the meeting",
        user_id="user123",
        context={"preferences": {}}
    )
    
    print(f"Task result: {result}")

if __name__ == "__main__":
    asyncio.run(main())

