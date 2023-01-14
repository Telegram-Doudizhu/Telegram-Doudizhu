from fun.rooms import *

import logging
logger = logging.getLogger(__name__)

from telegram import Update
from telegram.ext import Application, CommandHandler, InlineQueryHandler, ContextTypes

async def new_game() -> None:
    return

async def join_game() -> None:
    return

async def kill_game() -> None:
    return

async def help() -> None:
    return

async def inline_query() -> None:
    return

def start_bot(token:str, proxy:str = '') -> None:
    token,proxy = token.strip(),proxy.strip()
    logger.info('Telegram bot preparing to start......')
    
    app = Application.builder().token(token)
    if len(proxy) > 0:
        app = app.proxy_url(proxy)
    app = app.build()

    app.add_handler(CommandHandler("new", new_game))
    app.add_handler(CommandHandler("join", join_game))
    app.add_handler(CommandHandler("kill", kill_game))
    app.add_handler(CommandHandler("help", help))

    app.add_handler(InlineQueryHandler(inline_query))

    logger.warn('Telegram bot has started.')
    app.run_polling()