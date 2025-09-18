# 🔐 OAuth Setup Guide

## Environment Variables Required:

Add these environment variables in Railway:

### 1. **GOOGLE_CLIENT_ID**
- Your Google OAuth Client ID from Google Cloud Console

### 2. **GOOGLE_CLIENT_SECRET** 
- Your Google OAuth Client Secret from Google Cloud Console

## How to Add in Railway:

1. Go to Railway project dashboard
2. Click on your service
3. Go to "Variables" tab
4. Add both variables with your Google OAuth credentials
5. Railway will auto-redeploy

## Verification:

- Check `/health` endpoint for `google_client_id: true` and `google_client_secret: true`
- Test "connect my Gmail" command
- Should redirect to real Google OAuth

**The OAuth credentials you provided earlier will work perfectly! 🔐**
