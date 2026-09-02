import logging
import os

from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes

load_dotenv()

# -----------------------------
# CONFIG
# -----------------------------
BOT_TOKEN = (
    os.getenv("BOT_TOKEN")
    or os.getenv("TELEGRAM_BOT_TOKEN")
    or os.getenv("TOKEN")
    or os.getenv("API_TOKEN")
)

# Fixed BTC rate. It will NOT update automatically.
BTC_USD_RATE = 77000

USDT_TRC20_ADDRESS = "TTk9Dw8C3uiiUacChkMahjJ5KjZYFptusA"
BTC_ADDRESS = "bc1qqxxgppzsxccvxuavpk6ygttvekpskkaewrqmhy"

PLANS = {
    "monthly": {
        "name": "Monthly Plan",
        "usd": 50,
    },
    "lifetime": {
        "name": "Lifetime Plan",
        "usd": 180,
    },
}

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


START_TEXT = """🤖 <b>Meet MENTAL-TRADER BOT — Your MT5 Profit Engine</b>

Welcome! I’m an advanced robot-trader that integrates directly into your MetaTrader 5 (MT5) app. No external terminals, no manual trading — just pure algorithmic power working around the clock.

<b>What makes me different?</b>
⚡️ <b>MT5 Native Integration:</b> I run inside the MT5 app as an automated expert advisor.
📈 <b>High-Yield Strategy:</b> Designed to target 100–200% daily profit on your balance.
🛡️ <b>Smart Risk Controls:</b> Built-in stop-loss and capital protection logic.
🕒 <b>24/5 Auto-Trading:</b> I never sleep, never hesitate, and never let emotions ruin a trade."""


PLAN_TEXT = """💎 <b>Unlock Full Access — Choose Your Plan</b>

With daily targets of 100–200%, the subscription can pay for itself within the first trading session.

📅 <b>Monthly Plan — $50</b>
Perfect for testing the waters.

· Full MT5 integration for 30 days
· All strategies and auto-trading enabled
· Regular updates and support

♾️ <b>Lifetime Plan — $180</b>
Best value for serious traders.

· One-time payment, unlimited access
· All future updates included
· Priority support
· No recurring fees — ever

⚠️ Remember: trading involves risk. Past performance doesn’t guarantee future results. Only invest what you can afford to lose.

Ready to activate? Tap Choose Plan below and start your journey to automated profits! 🚀"""


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [[InlineKeyboardButton("GET BOT", callback_data="get_bot")]]

    await update.message.reply_text(
        START_TEXT,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def get_bot(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("MONTHLY 50$", callback_data="plan_monthly")],
        [InlineKeyboardButton("LIFETIME 180$", callback_data="plan_lifetime")],
    ]

    await query.edit_message_text(
        PLAN_TEXT,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def choose_plan(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    plan_key = query.data.removeprefix("plan_")

    if plan_key not in PLANS:
        return

    keyboard = [
        [
            InlineKeyboardButton(
                "USDT TRC20",
                callback_data=f"payment_usdt_{plan_key}",
            )
        ],
        [
            InlineKeyboardButton(
                "BTC",
                callback_data=f"payment_btc_{plan_key}",
            )
        ],
    ]

    await query.edit_message_text(
        "Select a payment method",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def payment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    parts = query.data.split("_", 2)
    if len(parts) != 3:
        return

    _, currency, plan_key = parts

    if plan_key not in PLANS:
        return

    usd_amount = PLANS[plan_key]["usd"]

    if currency == "usdt":
        amount_text = f"{usd_amount} USDT"
    elif currency == "btc":
        btc_amount = usd_amount / BTC_USD_RATE
        amount_text = f"{btc_amount:.8f} BTC"
    else:
        return

    keyboard = [[
        InlineKeyboardButton(
            "Get the address for payment",
            callback_data=f"address_{currency}_{plan_key}",
        )
    ]]

    await query.edit_message_text(
        f"Pay the amount: <b>{amount_text}</b>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def show_payment_address(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    query = update.callback_query
    await query.answer()

    parts = query.data.split("_", 2)
    if len(parts) != 3:
        return

    _, currency, plan_key = parts

    if plan_key not in PLANS:
        return

    usd_amount = PLANS[plan_key]["usd"]

    if currency == "usdt":
        amount_text = f"{usd_amount} USDT"
        wallet_address = USDT_TRC20_ADDRESS
    elif currency == "btc":
        btc_amount = usd_amount / BTC_USD_RATE
        amount_text = f"{btc_amount:.8f} BTC"
        wallet_address = BTC_ADDRESS
    else:
        return

    # Remove the button after it is pressed, keep the amount visible.
    await query.edit_message_text(
        f"Pay the amount: <b>{amount_text}</b>",
        parse_mode="HTML",
    )

    # Wallet address appears only after pressing the button.
    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text=f"<code>{wallet_address}</code>",
        parse_mode="HTML",
    )

    # Separate message requested by the user.
    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text="A payment notification will be sent automatically to the bot",
    )


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.exception(
        "Unhandled exception while processing an update:",
        exc_info=context.error,
    )


def main() -> None:
    if not BOT_TOKEN:
        raise RuntimeError(
            "Telegram token is not set. Set BOT_TOKEN (recommended) in Bothost environment variables."
        )

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(get_bot, pattern=r"^get_bot$"))
    app.add_handler(
        CallbackQueryHandler(
            choose_plan,
            pattern=r"^plan_(monthly|lifetime)$",
        )
    )
    app.add_handler(
        CallbackQueryHandler(
            payment,
            pattern=r"^payment_(usdt|btc)_(monthly|lifetime)$",
        )
    )
    app.add_handler(
        CallbackQueryHandler(
            show_payment_address,
            pattern=r"^address_(usdt|btc)_(monthly|lifetime)$",
        )
    )

    app.add_error_handler(error_handler)

    logger.info("MENTAL-TRADER BOT started")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
