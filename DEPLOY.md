# 🚀 Quick Deploy Guide

## Files in This Directory (Ready for GitHub):

✅ **Core System:**
- `web_app.py` - Flask web interface  
- `main_poke_agent.py` - Main conversational agent
- `execution_agent.py` - Task execution engine
- `COMPLETE_POKE_SYSTEM_PROMPT.txt` - Your complete original prompts

✅ **Services:**
- `email_service.py` - Gmail API integration
- `calendar_service.py` - Google Calendar API  
- `memory_manager.py` - User memory & context
- `trigger_manager.py` - Automations & reminders
- `integration_manager.py` - Notion/Linear/etc.

✅ **Web Interface:**
- `templates/chat.html` - iMessage-style UI
- `requirements.txt` - Python dependencies
- `Procfile` - Railway deployment config

## Deploy Steps:

1. **Upload to GitHub:**
   - Create new repository: `poke-real-system`
   - Upload ALL files from this directory
   - Don't skip any files - they're all needed

2. **Deploy to Railway:**
   - Connect GitHub repo to Railway
   - Add environment variables:
     ```
     OPENAI_API_KEY=your-openai-key
     GMAIL_CREDENTIALS=your-gmail-api-json
     GOOGLE_CALENDAR_CREDENTIALS=your-calendar-api-json
     ```
   - Deploy!

3. **Test:**
   - Visit your Railway URL
   - Should see "REAL SYSTEM ACTIVE" 
   - Try: "hey", "send an email", "check my calendar"

## File Count: 16 files total
This is a clean, minimal deployment with no extra files that could cause GitHub processing issues.

**Ready for production! 🎯**
