# MENTAL-TRADER BOT

## Files for GitHub
Upload:
- bot.py
- requirements.txt
- .gitignore
- .env.example
- README.md

Do NOT upload a real .env file or your Telegram bot token to GitHub.

## Bothost settings
- Git URL: your GitHub repository URL
- Branch: main
- Main file / entrypoint: bot.py
- Environment variable:
  BOT_TOKEN = your NEW BotFather token

## Payment flow
/start
→ GET BOT
→ MONTHLY 50$ / LIFETIME 180$
→ USDT TRC20 / BTC
→ "Pay the amount"
→ separate wallet-address message
→ END

BTC conversion is fixed at:
1 BTC = 77,000 USD

Thus:
$50  = 0.00064935 BTC
$180 = 0.00233766 BTC
