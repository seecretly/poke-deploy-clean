"""
Educational Poke Clone - Integration Manager
Handles external integrations like Notion, Linear, etc.
"""

import asyncio
import json
from typing import Dict, List, Optional, Any
from datetime import datetime

class IntegrationManager:
    """
    Integration manager for external services.
    """
    
    def __init__(self):
        self.integrations = {}  # Simple in-memory storage for demo
        
    async def search_notion(self, user_id: str, query: str) -> List[Dict]:
        """Search Notion pages/databases"""
        try:
            # Simulate Notion search results
            mock_results = [
                {
                    "id": "notion_001",
                    "title": "Project Planning Document",
                    "content": "This document contains our project planning details...",
                    "url": "https://notion.so/project-planning",
                    "last_modified": "2024-01-15T10:30:00Z",
                    "source": "notion"
                },
                {
                    "id": "notion_002", 
                    "title": "Meeting Notes - Q1 Planning",
                    "content": "Notes from our Q1 planning meeting...",
                    "url": "https://notion.so/meeting-notes",
                    "last_modified": "2024-01-14T15:45:00Z",
                    "source": "notion"
                }
            ]
            
            # Filter results based on query
            filtered_results = []
            query_lower = query.lower()
            
            for result in mock_results:
                if (query_lower in result["title"].lower() or 
                    query_lower in result["content"].lower()):
                    filtered_results.append(result)
            
            return filtered_results
            
        except Exception as e:
            print(f"Error searching Notion: {e}")
            return []
    
    async def search_linear(self, user_id: str, query: str) -> List[Dict]:
        """Search Linear issues/tasks"""
        try:
            # Simulate Linear search results
            mock_results = [
                {
                    "id": "linear_001",
                    "title": "Fix login bug",
                    "description": "Users are unable to login with certain credentials",
                    "status": "In Progress",
                    "priority": "High",
                    "assignee": "John Doe",
                    "url": "https://linear.app/issue/001",
                    "created_at": "2024-01-15T09:00:00Z",
                    "source": "linear"
                },
                {
                    "id": "linear_002",
                    "title": "Add dark mode support",
                    "description": "Implement dark mode theme for the application",
                    "status": "Todo",
                    "priority": "Medium",
                    "assignee": "Jane Smith",
                    "url": "https://linear.app/issue/002",
                    "created_at": "2024-01-14T14:20:00Z",
                    "source": "linear"
                }
            ]
            
            # Filter results based on query
            filtered_results = []
            query_lower = query.lower()
            
            for result in mock_results:
                if (query_lower in result["title"].lower() or 
                    query_lower in result["description"].lower()):
                    filtered_results.append(result)
            
            return filtered_results
            
        except Exception as e:
            print(f"Error searching Linear: {e}")
            return []
    
    async def search_vercel(self, user_id: str, query: str) -> List[Dict]:
        """Search Vercel deployments"""
        try:
            # Simulate Vercel search results
            mock_results = [
                {
                    "id": "vercel_001",
                    "name": "my-app-frontend",
                    "url": "https://my-app.vercel.app",
                    "status": "Ready",
                    "last_deployment": "2024-01-15T16:30:00Z",
                    "source": "vercel"
                }
            ]
            
            return mock_results
            
        except Exception as e:
            print(f"Error searching Vercel: {e}")
            return []
    
    async def get_integration_status(self, user_id: str) -> Dict:
        """Get status of all integrations for a user"""
        return {
            "notion": {"connected": True, "last_sync": "2024-01-15T10:30:00Z"},
            "linear": {"connected": True, "last_sync": "2024-01-15T09:15:00Z"},
            "vercel": {"connected": False, "last_sync": None},
            "intercom": {"connected": False, "last_sync": None},
            "sentry": {"connected": False, "last_sync": None}
        }

