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


def green_button(text: str, callback_data: str) -> InlineKeyboardButton:
    """Green action button on supported Telegram clients."""
    return InlineKeyboardButton(
        text,
        callback_data=callback_data,
        style="success",
    )


def back_button(callback_data: str) -> InlineKeyboardButton:
    """Neutral Back button."""
    return InlineKeyboardButton(
        "back",
        callback_data=callback_data,
    )


async def render_start_message(message) -> None:
    keyboard = [[green_button("GET BOT", "get_bot")]]

    await message.edit_text(
        START_TEXT,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def render_plan_message(message) -> None:
    keyboard = [
        [green_button("MONTHLY 50$", "plan_monthly")],
        [green_button("LIFETIME 180$", "plan_lifetime")],
        [back_button("back_start")],
    ]

    await message.edit_text(
        PLAN_TEXT,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def render_payment_method_message(message, plan_key: str) -> None:
    if plan_key not in PLANS:
        return

    keyboard = [
        [green_button("USDT TRC20", f"payment_usdt_{plan_key}")],
        [green_button("BTC", f"payment_btc_{plan_key}")],
        [back_button("back_plans")],
    ]

    await message.edit_text(
        "Select a payment method",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


def payment_amount(currency: str, plan_key: str) -> str | None:
    if plan_key not in PLANS:
        return None

    usd_amount = PLANS[plan_key]["usd"]

    if currency == "usdt":
        return f"{usd_amount} USDT"

    if currency == "btc":
        btc_amount = usd_amount / BTC_USD_RATE
        return f"{btc_amount:.8f} BTC"

    return None


async def render_amount_message(message, currency: str, plan_key: str) -> None:
    amount_text = payment_amount(currency, plan_key)
    if amount_text is None:
        return

    keyboard = [
        [
            green_button(
                "Get the address for payment",
                f"address_{currency}_{plan_key}",
            )
        ],
        [back_button(f"back_payment_{plan_key}")],
    ]

    await message.edit_text(
        f"Pay the amount: <b>{amount_text}</b>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [[green_button("GET BOT", "get_bot")]]

    await update.message.reply_text(
        START_TEXT,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def get_bot(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    await render_plan_message(query.message)


async def choose_plan(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    plan_key = query.data.removeprefix("plan_")
    await render_payment_method_message(query.message, plan_key)


async def payment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    parts = query.data.split("_", 2)
    if len(parts) != 3:
        return

    _, currency, plan_key = parts
    await render_amount_message(query.message, currency, plan_key)


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
    amount_text = payment_amount(currency, plan_key)

    if amount_text is None:
        return

    if currency == "usdt":
        wallet_address = USDT_TRC20_ADDRESS
    elif currency == "btc":
        wallet_address = BTC_ADDRESS
    else:
        return

    # After revealing the address, keep a Back button on the original message.
    await query.edit_message_text(
        f"Pay the amount: <b>{amount_text}</b>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(
            [[back_button(f"back_amount_{currency}_{plan_key}")]]
        ),
    )

    address_message = await context.bot.send_message(
        chat_id=query.message.chat_id,
        text=f"<code>{wallet_address}</code>",
        parse_mode="HTML",
    )

    notice_message = await context.bot.send_message(
        chat_id=query.message.chat_id,
        text="A payment notification will be sent automatically to the bot",
    )

    # Store these message IDs so Back can cleanly remove them.
    context.user_data["payment_extra_messages"] = [
        address_message.message_id,
        notice_message.message_id,
    ]


async def cleanup_payment_extra_messages(
    context: ContextTypes.DEFAULT_TYPE,
    chat_id: int,
) -> None:
    message_ids = context.user_data.pop("payment_extra_messages", [])

    for message_id in message_ids:
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
        except Exception:
            # If a message was already removed, navigation should still work.
            pass


async def back_navigation(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    query = update.callback_query
    await query.answer()

    data = query.data

    if data == "back_start":
        await render_start_message(query.message)
        return

    if data == "back_plans":
        await render_plan_message(query.message)
        return

    if data.startswith("back_payment_"):
        plan_key = data.removeprefix("back_payment_")
        await render_payment_method_message(query.message, plan_key)
        return

    if data.startswith("back_amount_"):
        parts = data.split("_", 3)
        if len(parts) != 4:
            return

        _, _, currency, plan_key = parts

        await cleanup_payment_extra_messages(
            context,
            query.message.chat_id,
        )
        await render_amount_message(query.message, currency, plan_key)


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
    app.add_handler(
        CallbackQueryHandler(
            back_navigation,
            pattern=r"^back_(start|plans|payment_(monthly|lifetime)|amount_(usdt|btc)_(monthly|lifetime))$",
        )
    )

    app.add_error_handler(error_handler)

    logger.info("MENTAL-TRADER BOT started")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
