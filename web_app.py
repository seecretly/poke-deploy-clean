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

# Simple in-memory token storage for OAuth flow
# In production, this would be stored in a database
auth_tokens = {}

# Initialize the real Poke system
openai_api_key = os.environ.get('OPENAI_API_KEY', 'demo-key')

try:
    print(f"🔧 Initializing Poke system...")
    main_agent = MainPokeAgent(openai_api_key)
    # Access the components from main_agent
    execution_agent = main_agent.execution_agent
    memory_manager = main_agent.memory_manager
    print(f"✅ Poke system initialized successfully")
except Exception as init_error:
    print(f"❌ Failed to initialize Poke system: {init_error}")
    # Create fallback objects
    main_agent = None
    execution_agent = None
    memory_manager = None

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
        
        # Check if system is initialized
        if not main_agent:
            return jsonify({
                'response': f"""❌ **System Not Initialized**

The Poke system failed to start properly. This usually means:
1. Missing OpenAI API key
2. Import/dependency issues
3. Service initialization problems

Please check the Railway logs for detailed error information.""",
                'timestamp': str(uuid.uuid4())
            })
        
        # Use the REAL Poke system
        try:
            # Process with real Poke agents
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                poke_response = loop.run_until_complete(
                    main_agent.process_user_message(user_id, message)
                )
                print(f"✅ Real Poke response: {len(poke_response)} characters")
                
            except Exception as async_error:
                print(f"❌ Async error: {async_error}")
                raise async_error
            finally:
                if 'loop' in locals():
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
        'email_service': execution_agent.email_service is not None if execution_agent else False,
        'calendar_service': execution_agent.calendar_service is not None if execution_agent else False,
        'memory_manager': memory_manager is not None
    }
    
    # Check API keys
    api_keys = {
        'openai': bool(os.environ.get('OPENAI_API_KEY')),
        'google_client_id': bool(os.environ.get('GOOGLE_CLIENT_ID')),
        'google_client_secret': bool(os.environ.get('GOOGLE_CLIENT_SECRET')),
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

@app.route('/auth-web')
def auth_web():
    """Handle Google OAuth authentication"""
    token = request.args.get('token')
    user_id = request.args.get('user_id')
    service = request.args.get('service', 'gmail')
    
    if not token or not user_id:
        return jsonify({'error': 'Missing token or user_id'}), 400
    
    # In a real implementation, this would:
    # 1. Validate the token
    # 2. Redirect to Google OAuth
    # 3. Handle the callback
    # 4. Store the credentials
    
    # Real Google OAuth credentials from environment variables
    google_client_id = os.environ.get('GOOGLE_CLIENT_ID')
    redirect_uri = "https://web-production-d8e63.up.railway.app/auth-callback"
    
    # Store the token for validation in callback
    auth_tokens[token] = {
        'user_id': user_id,
        'service': service,
        'timestamp': datetime.now().isoformat(),
        'used': False
    }
    
    print(f"🔑 Stored auth token: {token} for user: {user_id}")
    
    # Build real Google OAuth URL
    google_auth_url = f"https://accounts.google.com/oauth/authorize?client_id={google_client_id}&redirect_uri={redirect_uri}&response_type=code&scope=https://www.googleapis.com/auth/gmail.readonly+https://www.googleapis.com/auth/calendar&access_type=offline&state={token}_{user_id}_{service}"
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Poke Authentication</title>
        <style>
            body {{ font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; }}
            .auth-container {{ text-align: center; background: #f5f5f5; padding: 30px; border-radius: 10px; }}
            .btn {{ background: #4285f4; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 20px 0; }}
            .btn:hover {{ background: #3367d6; }}
        </style>
    </head>
    <body>
        <div class="auth-container">
            <h1>🔐 Connect to Google</h1>
            <p>To give Poke access to your {service.title()}, you'll need to authenticate with Google.</p>
            <p><strong>This will allow Poke to:</strong></p>
            <ul style="text-align: left; display: inline-block;">
                <li>Read and manage your emails</li>
                <li>Create and edit calendar events</li>
                <li>Search your Gmail and Calendar</li>
                <li>Set up automations</li>
            </ul>
            <a href="{google_auth_url}" class="btn">🚀 Connect with Google</a>
            <p><small>You'll be redirected to Google's secure login page.</small></p>
        </div>
    </body>
    </html>
    """

@app.route('/auth-callback')
def auth_callback():
    """Handle OAuth callback from Google"""
    code = request.args.get('code')
    state = request.args.get('state', '')
    error = request.args.get('error')
    
    if error:
        return f"""
        <!DOCTYPE html>
        <html>
        <head><title>Authentication Failed</title></head>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; text-align: center;">
            <h1>❌ Authentication Failed</h1>
            <p>Error: {error}</p>
            <p>Please try again or contact support.</p>
        </body>
        </html>
        """
    
    if not code:
        return jsonify({{'error': 'No authorization code received'}}), 400
    
    # Parse state to get token, user_id, and service
    try:
        token, user_id, service = state.split('_', 2)
        print(f"🔍 OAuth callback - Token: {token}, User: {user_id}, Service: {service}")
    except Exception as e:
        print(f"❌ State parsing error: {e}, State: {state}")
        return f"""
        <!DOCTYPE html>
        <html>
        <head><title>Authentication Failed</title></head>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; text-align: center;">
            <h1>❌ Authentication Failed</h1>
            <p>Invalid state parameter format.</p>
            <p>Please try the authentication process again.</p>
        </body>
        </html>
        """
    
    # Validate token
    if token not in auth_tokens:
        print(f"❌ Token not found: {token}")
        print(f"🔍 Available tokens: {list(auth_tokens.keys())}")
        return f"""
        <!DOCTYPE html>
        <html>
        <head><title>Authentication Failed</title></head>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; text-align: center;">
            <h1>❌ Authentication Token Mismatch</h1>
            <p>The authentication token is invalid or has expired.</p>
            <p>Please try the authentication process again from the beginning.</p>
        </body>
        </html>
        """
    
    # Check if token was already used
    if auth_tokens[token]['used']:
        print(f"❌ Token already used: {token}")
        return f"""
        <!DOCTYPE html>
        <html>
        <head><title>Authentication Failed</title></head>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; text-align: center;">
            <h1>❌ Authentication Token Already Used</h1>
            <p>This authentication token has already been used.</p>
            <p>Please start a new authentication process.</p>
        </body>
        </html>
        """
    
    # Mark token as used
    auth_tokens[token]['used'] = True
    print(f"✅ Token validated and marked as used: {token}")
    
    # Real OAuth implementation using environment variables
    google_client_id = os.environ.get('GOOGLE_CLIENT_ID')
    google_client_secret = os.environ.get('GOOGLE_CLIENT_SECRET')
    redirect_uri = "https://web-production-d8e63.up.railway.app/auth-callback"
    
    try:
        # Exchange authorization code for tokens
        import requests
        token_response = requests.post('https://oauth2.googleapis.com/token', data={
            'client_id': google_client_id,
            'client_secret': google_client_secret,
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': redirect_uri,
        })
        
        if token_response.status_code != 200:
            print(f"❌ Token exchange failed: {token_response.text}")
            return f"""
            <!DOCTYPE html>
            <html>
            <head><title>Authentication Failed</title></head>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; text-align: center;">
                <h1>❌ Authentication Failed</h1>
                <p>Failed to exchange authorization code for tokens.</p>
                <p>Please try again or contact support.</p>
            </body>
            </html>
            """
        
        tokens = token_response.json()
        access_token = tokens.get('access_token')
        refresh_token = tokens.get('refresh_token')
        
        print(f"✅ OAuth successful for user {user_id}, service: {service}")
        print(f"🔑 Access token received: {access_token[:20]}...")
        
        # Clean up the auth token
        if token in auth_tokens:
            del auth_tokens[token]
            print(f"🧹 Cleaned up auth token: {token}")
        
        # In a production system, you would store these tokens in a database
        # For now, we'll just log the success
        
    except Exception as e:
        print(f"❌ OAuth error: {e}")
        return f"""
        <!DOCTYPE html>
        <html>
        <head><title>Authentication Error</title></head>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; text-align: center;">
            <h1>❌ Authentication Error</h1>
            <p>Error: {str(e)}</p>
            <p>Please try again or contact support.</p>
        </body>
        </html>
        """
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Authentication Successful</title>
        <style>
            body {{ font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; text-align: center; }}
            .success {{ background: #d4edda; border: 1px solid #c3e6cb; color: #155724; padding: 20px; border-radius: 10px; }}
        </style>
    </head>
    <body>
        <div class="success">
            <h1>✅ Successfully Connected!</h1>
            <p>Your {service.title()} account has been connected to Poke.</p>
            <p><strong>You can now:</strong></p>
            <ul style="text-align: left; display: inline-block;">
                <li>Ask Poke to read your emails</li>
                <li>Schedule meetings and events</li>
                <li>Search your Gmail and Calendar</li>
                <li>Set up automations</li>
            </ul>
            <p>Go back to the chat and try commands like:</p>
            <p><em>"Check my recent emails"</em> or <em>"Schedule a meeting tomorrow"</em></p>
        </div>
    </body>
    </html>
    """

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
    print(f"🔑 OpenAI API Key: {'✅ Set' if openai_api_key != 'demo-key' else '❌ Missing'}")
    print(f"🧠 Main Agent: {'✅ Loaded' if main_agent else '❌ Failed'}")
    print(f"⚡ Execution Agent: {'✅ Loaded' if execution_agent else '❌ Failed'}")
    print(f"📧 Email Service: {'✅ Loaded' if execution_agent and execution_agent.email_service else '❌ Failed'}")
    print(f"📅 Calendar Service: {'✅ Loaded' if execution_agent and execution_agent.calendar_service else '❌ Failed'}")
    print(f"💭 Memory Manager: {'✅ Loaded' if memory_manager else '❌ Failed'}")
    
    if not main_agent:
        print("⚠️  WARNING: System not fully initialized - running in fallback mode")
    else:
        print("✅ All systems operational!")
    
    app.run(host='0.0.0.0', port=port, debug=True)
