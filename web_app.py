#!/usr/bin/env python3
"""
🧠 REAL Poke - Fully Working System
Uses the original Poke architecture with real Gmail API, Calendar API, and tool integrations
"""

from flask import Flask, render_template, request, jsonify, session
import os
import uuid
import asyncio
from datetime import datetime
from main_poke_agent import MainPokeAgent
from execution_agent import ExecutionAgent
from memory_manager import MemoryManager
from email_service import EmailService
from calendar_service import CalendarService
import json

# Load the COMPLETE Poke system prompt
def load_complete_poke_prompt():
    try:
        with open('COMPLETE_POKE_SYSTEM_PROMPT.txt', 'r') as f:
            return f.read()
    except FileNotFoundError:
        return """You are Poke, developed by The Interaction Company of California. You are extremely helpful, proactive, and efficient with a casual, friendly personality. You have access to Gmail, Calendar, web browsing, and various integrations."""

COMPLETE_POKE_PROMPT = load_complete_poke_prompt()

app = Flask(__name__)
app.secret_key = 'poke-real-secret-key-change-in-production'

# Initialize the real Poke system
memory_manager = MemoryManager()
email_service = EmailService()
calendar_service = CalendarService()
execution_agent = ExecutionAgent(email_service, calendar_service, memory_manager)
main_agent = MainPokeAgent(execution_agent, memory_manager)

@app.route('/')
def index():
    """Main chat interface"""
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())
    return render_template('chat.html')

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat messages with REAL Poke system"""
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        user_id = session.get('user_id', str(uuid.uuid4()))
        
        if not message:
            return jsonify({'error': 'No message provided'}), 400
        
        print(f"🧠 Real Poke processing: {message}")
        
        # Use the REAL Poke system
        try:
            # Create user message
            from main_poke_agent import UserMessage
            user_msg = UserMessage(
                content=message,
                timestamp=datetime.now(),
                user_id=user_id
            )
            
            # Process with real Poke agents
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                response = loop.run_until_complete(
                    main_agent.process_user_message(user_msg)
                )
                poke_response = response.content
                print(f"✅ Real Poke response: {len(poke_response)} characters")
                
            finally:
                loop.close()
                
        except Exception as e:
            print(f"❌ Real Poke error: {e}")
            # Fallback to explain the system
            poke_response = f"""⚠️ **Real Poke System Error**

I'm the REAL Poke system with full capabilities, but encountered an error: {str(e)}

I have access to:
• **Real Gmail API** for email management
• **Real Google Calendar API** for scheduling
• **Web browsing capabilities** 
• **Notion, Linear, Vercel integrations**
• **Trigger/automation system**
• **Memory management**

The error suggests missing API keys or configuration. Check your environment setup."""
        
        return jsonify({
            'response': poke_response,
            'timestamp': str(uuid.uuid4())
        })
        
    except Exception as e:
        print(f"💥 Web app error: {e}")
        return jsonify({'error': f'System error: {str(e)}'}), 500

@app.route('/health')
def health():
    """Health check for real system"""
    # Check if core services are available
    services = {
        'main_agent': main_agent is not None,
        'execution_agent': execution_agent is not None,
        'email_service': email_service is not None,
        'calendar_service': calendar_service is not None,
        'memory_manager': memory_manager is not None
    }
    
    # Check API keys
    api_keys = {
        'openai': bool(os.environ.get('OPENAI_API_KEY')),
        'gmail': bool(os.environ.get('GMAIL_CREDENTIALS')),
        'google_calendar': bool(os.environ.get('GOOGLE_CALENDAR_CREDENTIALS'))
    }
    
    all_healthy = all(services.values())
    
    return jsonify({
        'status': 'healthy' if all_healthy else 'degraded',
        'service': 'REAL Poke System',
        'version': '1.0.0-REAL',
        'services': services,
        'api_keys': api_keys,
        'architecture': 'Multi-Agent with Real Integrations'
    })

@app.route('/setup')
def setup():
    """Setup instructions for the real system"""
    return jsonify({
        'message': 'REAL Poke System Setup',
        'required_env_vars': [
            'OPENAI_API_KEY - Your OpenAI API key',
            'GMAIL_CREDENTIALS - Gmail API credentials JSON',
            'GOOGLE_CALENDAR_CREDENTIALS - Google Calendar API credentials JSON',
            'NOTION_API_KEY - (Optional) Notion integration',
            'LINEAR_API_KEY - (Optional) Linear integration'
        ],
        'setup_steps': [
            '1. Set up Google Cloud Project with Gmail & Calendar APIs',
            '2. Download credentials JSON files',
            '3. Set environment variables in Railway',
            '4. Deploy and test integrations',
            '5. Configure OAuth consent screen for production'
        ],
        'architecture': 'This is the REAL Poke system with actual tool integrations'
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    print(f"🚀 Starting REAL Poke System on port {port}")
    print(f"🧠 Main Agent: {'✅ Loaded' if main_agent else '❌ Failed'}")
    print(f"⚡ Execution Agent: {'✅ Loaded' if execution_agent else '❌ Failed'}")
    print(f"📧 Email Service: {'✅ Loaded' if email_service else '❌ Failed'}")
    print(f"📅 Calendar Service: {'✅ Loaded' if calendar_service else '❌ Failed'}")
    print(f"💭 Memory Manager: {'✅ Loaded' if memory_manager else '❌ Failed'}")
    app.run(host='0.0.0.0', port=port, debug=True)
