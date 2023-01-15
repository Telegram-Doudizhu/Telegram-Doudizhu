from uuid import uuid4
from cls.room import Room
from fun.rooms import *

import logging
logger = logging.getLogger(__name__)

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultArticle, InputTextMessageContent, Update
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, InlineQueryHandler, ContextTypes

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    '''
        Start command handler
    '''
    await update.message.reply_text("Started.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    '''
        Help command handler
        show detailed usage of the bot
    '''
    await update.message.reply_text("Use /start to test this bot.")


# buttons for callback query
class Button:
    (
        User1,
        User2,
        User3,
        Settings,
        Start,
    ) = map(chr, range(0x41, 0x46))
    nHHard = 0x60
    HBack = chr(0x70)
    
def CON_CBD(roomid: str, msg: str, msg1:str = ''):
    '''
        Construct callback data for a button
    '''
    return f"{roomid}|{msg}|{msg1}"

def DES_CBD(data: str):
    '''
        Destruct callback data
    '''
    return data.split('|')

async def GEN_KBD(room: Room) -> InlineKeyboardMarkup:
    '''
        Generate keyboard for room management
    '''
    keyboard = [
        [ InlineKeyboardButton(room.owner.name, callback_data = CON_CBD(room.id, Button.User1)), ],
        [ InlineKeyboardButton("Click to join" if room.user1 is None else room.user1.name, callback_data = CON_CBD(room.id, Button.User2)), ],
        [ InlineKeyboardButton("Click to join" if room.user2 is None else room.user2.name, callback_data = CON_CBD(room.id, Button.User3)), ],
        [ InlineKeyboardButton("Settings", callback_data = CON_CBD(room.id, Button.Settings)), ],
        [ InlineKeyboardButton("Start!", callback_data = CON_CBD(room.id, Button.Start)), ],
    ]
    return InlineKeyboardMarkup(keyboard)

async def GEN_KBD_HARD(room: Room, parent: str) -> InlineKeyboardMarkup:
    '''
        Generate keyboard for hard mode selection
    '''
    keyboard = []
    for i, name in enumerate(Room.Robot.hard_list):
        keyboard.append([ InlineKeyboardButton(name, callback_data = CON_CBD(room.id, parent, chr(Button.nHHard + i))), ])
    keyboard.append([ InlineKeyboardButton("Back", callback_data = CON_CBD(room.id, parent, Button.HBack)), ])
    return InlineKeyboardMarkup(keyboard)


async def new_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    '''
        /new command handler
        create a new room, with the caller as the owner (first player)
        replied with buttons:
            - users: three buttons with representing users (updated when joining)
            - - join: join in this place
            - - add a robot: add a robot in this place
            - - leave: leave this room (destroy the room when the owner exits)
            - settings: trigger /settings inline query
            - start: start the game (available when three players joined)
    '''
    room = Room.create(update.message.chat_id, Room.User(update.effective_user.id, f"User @{update.effective_user.username}"))
    if room is False:
        await update.message.reply_text("You are already in a room.")
        return
    logger.info(f"Room created: {room.id}, owner: {room.owner.name}")
    reply_markup = await GEN_KBD(room)
    await update.message.reply_text("A new room has been created for you.", reply_markup = reply_markup)

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    '''
        Callback handler
        used in room management
    '''
    query = update.callback_query
    
    async def error(msg: str):
        await query.edit_message_text(text = "Internal error has occurred.\n" + str)

    roomid, msg, msg1 = DES_CBD(query.data)
    room = Room.from_roomid(roomid)
    if room is None:
        await query.edit_message_text(text = "This room has been destroyed.")
        await query.answer()
        return
    if room.state != Room.STATE_JOINING:
        error(f"Room state mismatch, STATUS_JOINING expected, int:{room.state} given")
        await query.answer()
        return
    
    text = None
    match msg:
        case Button.User1:
            if query.from_user.id == room.owner.id:
                logger.info(f"Room destroyed: {room.id}, owner: {room.owner.name} left")
                room.destroy(); del room
                await query.edit_message_text(text = "The owner has left the room.")
        
        case Button.User2 | Button.User3:
            pos = 2 if msg == Button.User2 else 3
            occupied = bool(room.users[pos - 1] is not None)
            join = room.join1 if msg == Button.User2 else room.join2
            leave = room.leave1 if msg == Button.User2 else room.leave2
            refresh = False
            if not occupied and query.from_user.id == room.owner.id:
                match msg1:
                    case '':
                        reply_markup = await GEN_KBD_HARD(room, msg)
                        await query.edit_message_text(text = "Select a hard mode for the robot.", reply_markup = reply_markup)
                    case Button.HBack:
                        refresh = True
                    case msg1 if msg1 in map(chr, range(Button.nHHard, Button.nHHard + len(Room.Robot.hard_list))):
                        robot = Room.Robot(ord(msg1) - Button.nHHard)
                        leave() # force leave
                        if (ret:=join(robot)) is True:
                            refresh = True
                            logger.info(f"Robot {robot.name} joined in room {room.id}, pos:{pos}")
                            text = f"Robot {robot.name} joined in pos:{pos}."
                        else:
                            text = ret  
                    case _:
                        error("Invalid button ({msg}) pressed.")
            elif msg1 != '':
                pass
            elif occupied and query.from_user.id == room.owner.id:
                refresh = True
                name = room.users[pos - 1].name
                if (ret:=leave()) is True:
                    logger.info(f"Kick user {name} from room {room.id}, pos:{pos}")
                    text = f"Kicked user {name} from room."
                else:
                    text = ret
            elif occupied and (query.from_user.id == room.users[pos - 1].id):
                refresh = True
                name = room.users[pos - 1].name
                if (ret:=leave()) is True:
                    logger.info(f"User left {name}, room {room.id}, pos:{pos}")
                    text = f"You have left the room."
                else:
                    text = ret
            elif not occupied:
                refresh = True
                if (ret:=join(Room.User(query.from_user.id, f"User @{query.from_user.username}"))) is True:
                    logger.info(f"User joined {room.users[pos - 1].name}, room {room.id}, pos:{pos}")
                    text = f"You have joined the room in pos:{pos}."
                else:
                    text = ret
            else:
                text = "This place is occupied."
            if refresh:
                reply_markup = await GEN_KBD(room)
                await query.edit_message_text(text = "A new room has been created for you.", reply_markup = reply_markup)
        
        case Button.Settings:
            if query.from_user.id == room.owner.id:
                text = "NOT IMPLEMENTED" # TODO
            else:
                text = "You are not the owner."
        
        case Button.Start:
            if query.from_user.id == room.owner.id:
                if (ret:=room.start()) is True:
                    logger.info(f"Room started: {room.id}.")
                    await query.edit_message_text(text = "This room has started.")
                else:
                    text = ret
        case _:
            error("Invalid button ({msg}) pressed.")
    
    await query.answer(text)

async def inline_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    '''
        Inline query handler
        used for extended card selection
    '''
    return

def remove_job_if_exists(name: str, context: ContextTypes.DEFAULT_TYPE) -> bool:
    '''
        Remove job with given name.
        clear timeout counting
    '''
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True

async def alarm(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send the alarm message."""
    job = context.job
    await context.bot.send_message(job.chat_id, text=f"Beep! {repr(job.data)} seconds are over! {repr(context.user_data)}")
    keyboard = [
        [
            InlineKeyboardButton("f", callback_data="f"),
            InlineKeyboardButton("b", callback_data="b"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await job.data.edit_text(
        text=f"Edited whatever", reply_markup=reply_markup
    )

def start_bot(token:str, proxy:str = '') -> None:
    '''
        Start the bot (main entrance)
    '''
    token,proxy = token.strip(),proxy.strip()
    logger.info("Telegram bot preparing to start")
    
    app = Application.builder().token(token)
    if len(proxy) > 0:
        app = app.proxy_url(proxy)
    app = app.build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("new", new_command))
    app.add_handler(CallbackQueryHandler(callback_handler))
    app.add_handler(InlineQueryHandler(inline_handler))

    logger.warning("Telegram bot has started")
    app.run_polling()

__all__ = ('start_bot', )
