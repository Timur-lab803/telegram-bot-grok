Grok Telegram Webhook Bot (Vercel-ready)

Files:
- api/index.py       - Flask webhook handler for Telegram
- requirements.txt
- vercel.json
- .gitignore

Instructions:
1) Create a GitHub repo and push these files.
2) On Vercel, import the GitHub repo and deploy.
3) In Vercel dashboard, set Environment Variables:
   TELEGRAM_TOKEN  - your bot token
   GROK_API_KEY    - your Grok API key
   GROK_API_URL    - optional (default https://api.grok.ai/v1/generate)
4) After deploy, set Telegram webhook:
   https://api.telegram.org/bot<TELEGRAM_TOKEN>/setWebhook?url=https://<your-project>.vercel.app/webhook
