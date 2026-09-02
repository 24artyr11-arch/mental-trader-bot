# MENTAL-TRADER BOT

## GitHub files
Upload these files to the root of your repository:
- bot.py
- requirements.txt
- .gitignore
- .env.example
- README.md

Do NOT upload a real .env file or your Telegram bot token to GitHub.

## Bothost
Environment variable:
BOT_TOKEN = your NEW BotFather token

Branch:
main

Entrypoint:
bot.py

## Flow
/start
→ GET BOT
→ MONTHLY 50$ / LIFETIME 180$
→ USDT TRC20 / BTC
→ Pay the amount + button "Get the address for payment"
→ wallet address
→ separate message:
  A payment notification will be sent automatically to the bot
→ END

Fixed BTC rate:
1 BTC = 77,000 USD

$50 = 0.00064935 BTC
$180 = 0.00233766 BTC
