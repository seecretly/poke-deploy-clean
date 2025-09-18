"""
Educational Poke Clone - Calendar Service
Handles calendar operations including creating, editing, and searching events.
"""

import asyncio
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass

@dataclass
class CalendarEvent:
    """Represents a calendar event"""
    id: str
    title: str
    start_time: datetime
    end_time: datetime
    description: str
    location: Optional[str] = None
    attendees: List[str] = None

class CalendarService:
    """
    Calendar service for managing calendar operations.
    Handles Google Calendar API integration and event management.
    """
    
    def __init__(self):
        self.calendar_credentials = {}  # Will be loaded from config
        self.events_cache = {}  # Simple in-memory cache for demo
        
    async def create_event(self, title: str, date: str, time: str, description: str, user_id: str, **kwargs) -> Dict:
        """
        Create a new calendar event.
        """
        try:
            # Parse date and time
            start_datetime = self._parse_datetime(date, time)
            end_datetime = start_datetime + timedelta(hours=1)  # Default 1-hour duration
            
            # Create event object
            event = CalendarEvent(
                id=f"event_{datetime.now().timestamp()}",
                title=title,
                start_time=start_datetime,
                end_time=end_datetime,
                description=description,
                location=kwargs.get("location"),
                attendees=kwargs.get("attendees", [])
            )
            
            # Store in cache (in real implementation, use Google Calendar API)
            if user_id not in self.events_cache:
                self.events_cache[user_id] = []
            
            self.events_cache[user_id].append({
                "id": event.id,
                "title": event.title,
                "start_time": event.start_time.isoformat(),
                "end_time": event.end_time.isoformat(),
                "description": event.description,
                "location": event.location,
                "attendees": event.attendees
            })
            
            return {
                "success": True,
                "event_id": event.id,
                "details": f"Event '{title}' created for {start_datetime.strftime('%Y-%m-%d %H:%M')}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def update_event(self, event_id: str, updates: Dict, user_id: str) -> Dict:
        """
        Update an existing calendar event.
        """
        try:
            # Find the event in cache
            user_events = self.events_cache.get(user_id, [])
            event = next((e for e in user_events if e["id"] == event_id), None)
            
            if not event:
                return {"success": False, "error": "Event not found"}
            
            # Update event fields
            for key, value in updates.items():
                if key in event:
                    event[key] = value
            
            return {
                "success": True,
                "event_id": event_id,
                "details": f"Event updated successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def delete_event(self, event_id: str, user_id: str) -> Dict:
        """
        Delete a calendar event.
        """
        try:
            # Find and remove the event from cache
            user_events = self.events_cache.get(user_id, [])
            event = next((e for e in user_events if e["id"] == event_id), None)
            
            if not event:
                return {"success": False, "error": "Event not found"}
            
            user_events.remove(event)
            
            return {
                "success": True,
                "event_id": event_id,
                "details": f"Event '{event['title']}' deleted"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def search_events(self, user_id: str, query: str, limit: int = 10) -> List[Dict]:
        """
        Search calendar events based on a query.
        """
        try:
            user_events = self.events_cache.get(user_id, [])
            
            # Filter events based on query
            filtered_events = []
            query_lower = query.lower()
            
            for event in user_events:
                if (query_lower in event["title"].lower() or 
                    query_lower in event["description"].lower() or
                    query_lower in event.get("location", "").lower()):
                    filtered_events.append(event)
            
            return filtered_events[:limit]
            
        except Exception as e:
            print(f"Error searching events: {e}")
            return []
    
    async def get_upcoming_events(self, user_id: str, days: int = 7) -> List[Dict]:
        """
        Get upcoming events for the next N days.
        """
        try:
            user_events = self.events_cache.get(user_id, [])
            now = datetime.now()
            future_cutoff = now + timedelta(days=days)
            
            upcoming_events = []
            for event in user_events:
                event_time = datetime.fromisoformat(event["start_time"])
                if now <= event_time <= future_cutoff:
                    upcoming_events.append(event)
            
            # Sort by start time
            upcoming_events.sort(key=lambda x: x["start_time"])
            
            return upcoming_events
            
        except Exception as e:
            print(f"Error getting upcoming events: {e}")
            return []
    
    async def get_events_by_date(self, user_id: str, date: str) -> List[Dict]:
        """
        Get all events for a specific date.
        """
        try:
            user_events = self.events_cache.get(user_id, [])
            target_date = datetime.fromisoformat(date).date()
            
            events_for_date = []
            for event in user_events:
                event_date = datetime.fromisoformat(event["start_time"]).date()
                if event_date == target_date:
                    events_for_date.append(event)
            
            # Sort by start time
            events_for_date.sort(key=lambda x: x["start_time"])
            
            return events_for_date
            
        except Exception as e:
            print(f"Error getting events by date: {e}")
            return []
    
    async def create_recurring_event(self, title: str, start_date: str, start_time: str, 
                                   description: str, recurrence: str, user_id: str) -> Dict:
        """
        Create a recurring calendar event.
        """
        try:
            # Parse recurrence pattern
            if recurrence == "daily":
                frequency = timedelta(days=1)
            elif recurrence == "weekly":
                frequency = timedelta(weeks=1)
            elif recurrence == "monthly":
                frequency = timedelta(days=30)  # Simplified
            else:
                return {"success": False, "error": "Unsupported recurrence pattern"}
            
            # Create the first event
            start_datetime = self._parse_datetime(start_date, start_time)
            
            # Create multiple events based on recurrence
            events_created = []
            current_date = start_datetime
            
            for i in range(10):  # Create 10 recurring events
                event_result = await self.create_event(
                    title=f"{title} (Recurring {i+1})",
                    date=current_date.strftime("%Y-%m-%d"),
                    time=current_date.strftime("%H:%M"),
                    description=description,
                    user_id=user_id
                )
                
                if event_result["success"]:
                    events_created.append(event_result["event_id"])
                
                current_date += frequency
            
            return {
                "success": True,
                "events_created": len(events_created),
                "details": f"Created {len(events_created)} recurring events"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def find_free_time(self, user_id: str, duration_hours: int = 1, 
                           start_date: str = None, end_date: str = None) -> List[Dict]:
        """
        Find free time slots for scheduling.
        """
        try:
            if not start_date:
                start_date = datetime.now().strftime("%Y-%m-%d")
            if not end_date:
                end_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
            
            # Get all events in the date range
            all_events = []
            current_date = datetime.fromisoformat(start_date)
            end_date_obj = datetime.fromisoformat(end_date)
            
            while current_date <= end_date_obj:
                date_events = await self.get_events_by_date(user_id, current_date.strftime("%Y-%m-%d"))
                all_events.extend(date_events)
                current_date += timedelta(days=1)
            
            # Find free time slots (simplified algorithm)
            free_slots = []
            # This is a simplified implementation - in reality, you'd need
            # more sophisticated scheduling logic
            
            return free_slots
            
        except Exception as e:
            print(f"Error finding free time: {e}")
            return []
    
    def _parse_datetime(self, date: str, time: str) -> datetime:
        """
        Parse date and time strings into a datetime object.
        """
        try:
            # Handle different date formats
            if "/" in date:
                date_obj = datetime.strptime(date, "%m/%d/%Y")
            elif "-" in date:
                date_obj = datetime.strptime(date, "%Y-%m-%d")
            else:
                date_obj = datetime.strptime(date, "%Y-%m-%d")
            
            # Handle different time formats
            if ":" in time:
                time_obj = datetime.strptime(time, "%H:%M").time()
            else:
                time_obj = datetime.strptime(time, "%I:%M %p").time()
            
            return datetime.combine(date_obj.date(), time_obj)
            
        except Exception as e:
            raise ValueError(f"Invalid date/time format: {date} {time}")
    
    async def get_event_details(self, event_id: str, user_id: str) -> Optional[Dict]:
        """
        Get full details of a specific event.
        """
        try:
            user_events = self.events_cache.get(user_id, [])
            event = next((e for e in user_events if e["id"] == event_id), None)
            
            return event
            
        except Exception as e:
            print(f"Error getting event details: {e}")
            return None

# Example usage
async def main():
    """Example of how to use the CalendarService"""
    service = CalendarService()
    
    # Create an event
    result = await service.create_event(
        title="Team Meeting",
        date="2024-01-20",
        time="14:00",
        description="Weekly team standup",
        user_id="user123"
    )
    print(f"Create result: {result}")
    
    # Search events
    events = await service.search_events("user123", "meeting")
    print(f"Search results: {events}")

if __name__ == "__main__":
    asyncio.run(main())

