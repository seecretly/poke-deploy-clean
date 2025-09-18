# 🧠 REAL Poke - Fully Working AI Assistant

This is the **REAL, FULLY WORKING** Poke system with actual integrations, not a demo or simulation.

## ⚡ What Makes This REAL:

- ✅ **COMPLETE Original System Prompts** - All 6 parts combined into one file
- ✅ **Real Gmail API** integration for actual email management
- ✅ **Real Google Calendar API** for actual scheduling  
- ✅ **Real web browsing** capabilities
- ✅ **Real Notion/Linear/Vercel** integrations
- ✅ **Real trigger/automation** system
- ✅ **Real memory management** with persistent storage
- ✅ **Real dual-agent architecture** (Main + Execution)
- ✅ **Full Poke Personality** - Witty, warm, conversational, no corporate jargon

## 🏗️ Architecture:

```
User → Web Interface → Main Poke Agent → Execution Agent → Real APIs
                                    ↓
                              Memory Manager
```

## 🚀 Quick Deploy to Railway:

1. **Upload these files** to GitHub repository
2. **Connect to Railway**
3. **Set environment variables:**
   - `OPENAI_API_KEY` - Your OpenAI API key
   - `GMAIL_CREDENTIALS` - Gmail API credentials JSON
   - `GOOGLE_CALENDAR_CREDENTIALS` - Google Calendar API credentials JSON
4. **Deploy!**

## 📋 Required Setup:

### Google Cloud Console:
1. Create new project
2. Enable Gmail API and Google Calendar API  
3. Create OAuth 2.0 credentials
4. Download credentials JSON
5. Set up OAuth consent screen

### Environment Variables:
```bash
OPENAI_API_KEY=sk-proj-your-key-here
GMAIL_CREDENTIALS={"type":"service_account",...}
GOOGLE_CALENDAR_CREDENTIALS={"type":"service_account",...}
```

### Optional Integrations:
```bash
NOTION_API_KEY=secret_your-notion-key
LINEAR_API_KEY=lin_api_your-linear-key
VERCEL_TOKEN=your-vercel-token
```

## 🧪 Test Commands:

Once deployed, try these **REAL** commands:

- **"Check my recent emails"** → Actually searches Gmail
- **"Schedule a meeting tomorrow at 2pm"** → Actually creates calendar event
- **"Send an email to john@example.com"** → Actually composes and sends
- **"Find my Notion notes about the project"** → Actually searches Notion
- **"Set a reminder for next week"** → Actually creates trigger

## 🔧 Troubleshooting:

- Visit `/health` to check system status
- Visit `/setup` for detailed setup instructions  
- Check Railway logs for API connection issues

## ⚠️ Important:

This is the **REAL system** - it will actually perform actions like sending emails, creating calendar events, and modifying your data. Use with caution in production.

**No more demos or simulations - this is the full Poke experience! 🎯**