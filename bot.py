#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Telegram bot to play UNO in group chats

import logging
import os
from telegram.ext import Updater, InlineQueryHandler, ChosenInlineResultHandler
from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackQueryHandler

import config
from actions import *
from game_manager import game_manager
from internationalization import _

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = config.TOKEN

if not TOKEN:
    raise ValueError("No TOKEN found! Please set TOKEN in Heroku Config Vars.")

def main():
    updater = Updater(token=TOKEN, use_context=True)
    dp = updater.dispatcher

    # === All Handlers (from original bot) ===
    dp.add_handler(CommandHandler("start", start_game))
    dp.add_handler(CommandHandler("help", help_handler))
    dp.add_handler(CommandHandler("new", new_game))
    dp.add_handler(CommandHandler("join", join_game))
    dp.add_handler(CommandHandler("go", go_game))
    dp.add_handler(CommandHandler("kill", kill_game))
    dp.add_handler(CommandHandler("stats", stats))
    dp.add_handler(CommandHandler("mode", mode))
    dp.add_handler(CommandHandler("kick", kick_player))
    dp.add_handler(CommandHandler("open", open_lobby))
    dp.add_handler(CommandHandler("close", close_lobby))
    dp.add_handler(CommandHandler("lang", select_language))

    dp.add_handler(InlineQueryHandler(inline_query))
    dp.add_handler(ChosenInlineResultHandler(chosen_inline_result))
    dp.add_handler(CallbackQueryHandler(button))   # Important for card buttons

    dp.add_handler(MessageHandler(Filters.status_update.new_chat_members, new_player))
    dp.add_handler(MessageHandler(Filters.text & \~Filters.command, button))  # Fixed line

    # === HEROKU WEBHOOK (Critical) ===
    if __name__ == '__main__':
        port = int(os.environ.get("PORT", 8443))
        app_name = os.environ.get("HEROKU_APP_NAME")

        if app_name:
            webhook_url = f"https://{app_name}.herokuapp.com/{TOKEN}"
            updater.start_webhook(
                listen="0.0.0.0",
                port=port,
                url_path=TOKEN,
                webhook_url=webhook_url
            )
            logger.info(f"✅ Webhook started → {webhook_url}")
        else:
            # Local testing
            updater.start_polling()
            logger.info("🚀 Running locally with polling")

        updater.idle()

if __name__ == '__main__':
    main()