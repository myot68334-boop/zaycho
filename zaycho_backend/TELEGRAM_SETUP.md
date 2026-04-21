# Telegram Bot Setup

## 1. Create a bot with BotFather

1. Open Telegram
2. Search for `@BotFather`
3. Send `/newbot`
4. Enter your bot name
5. Enter your bot username
6. Copy the bot token

## 2. Set environment variables

Copy `.env.example` and fill these values:

- `PUBLIC_BASE_URL`
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_BOT_USERNAME`

Example:

```env
PUBLIC_BASE_URL=https://your-render-url.onrender.com
TELEGRAM_BOT_TOKEN=123456:ABC-your-token
TELEGRAM_BOT_USERNAME=your_bot_username
```

## 3. Restart the server

After saving env values, restart the FastAPI server.

## 4. Open admin panel

1. Log in with the admin account
2. Open the admin section
3. Find the `Telegram Bot` panel
4. Click `Set Telegram Webhook`

If setup succeeds, the webhook URL and bot link will appear.

## 5. Test the bot

1. Open your bot in Telegram
2. Send `/start`
3. Send a shopping question like:
   - `recommend skincare`
   - `suggest an outfit`

The bot will reply using the same ZayCho assistant logic.
